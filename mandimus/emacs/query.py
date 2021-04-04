#!/usr/bin/env python
# -*- coding: utf-8 -*-

from talon import Module, Context, cron, resource
from typing import Union, List, Dict, TypeVar, Set, Tuple, Optional
from user.knausj_talon.mandimus.emacs.connection import runEmacsCmd
from user.knausj_talon.mandimus.emacs.word_utils import decamelize, decamelize_words_only, count_category_transitions
from user.knausj_talon.code.keys import alphabet
import logging as log
import re
import string
from copy import copy
import functools
from pprint import pprint
import json
import math

# TODO: normalize pronunciations based on homophones
# TODO: normalize pronunciations by removing redundant S's

with resource.open("bigrams.json", 'r') as f:
    bigrams = json.load(f)

with resource.open("/usr/share/dict/words", 'r') as f:
    english_words = f.readlines()
    english_words = {word.strip().lower() for word in english_words}
    english_words.update([
        "arg",
        "args",
        "allocator",
        "const",
        "profiler",
        "uncast",
        "rehash",
        "tuple",
        "utils",
        "util",
        "dict"
        "sigsegv",
        "multicast",
        "matic",
        "microbench",
        "vec",
        "deque",
        "radix",
        "jupyter",
        "numexpr",
        "mandimus",
        "todo",
        "assign",
        "structs"
    ])
    to_remove = [
        "oma",
        "ra",
        "dix",
    ]
    for word in to_remove:
        try:
            english_words.remove(word)
        except KeyError:
            continue

bigrams_total = sum([v for b,v in bigrams.items()])

def compute_average_entropy_impl(s):
    global bigrams, bigrams_total
    total = 0
    for bigram in zip(s, s[1:]):
        if " " in bigram:
            continue
        # treat any missing bigrams as very rare
        apparent_bigram = bigram if bigram in bigrams else "zx"
        p = bigrams[apparent_bigram] / bigrams_total
        total += (p*math.log(p, 2))
    e = -total / len(s)
#    log.info(f"Word: {s} Entropy: {e}")
    return e

def compute_average_entropy(s):
    s = s.lower()
    # deal with cute naming like "kube" instead of "cube"
    return min(compute_average_entropy_impl(s),
               compute_average_entropy_impl(s.replace("c", "k")),
               compute_average_entropy_impl(s.replace("k", "c")))

word_substitutions = {
    "py" : "pie",
    "ptr" : "pointer",
    "trd" : "trade",
    "sigsegv" : "sig seg v",
    "matic" : "matt tick",
    "ctl" : "control",
    "lib" : "library",
    "std" : "standard",
    "bld" : "build",
    "msg" : "message",
    "sig" : "signal",
    "hdr" : "header",
    "memcpy" : "memory copy",
    "memcpys" : "memory copies",
}
word_substitutions.update({v:k for k,v in alphabet.items()})
english_words.update(word_substitutions.keys())
english_words.update(word_substitutions.values())

delete_punctuation = "".maketrans(string.punctuation, " "*len(string.punctuation))

def is_float_str(word: str) -> bool:
    try:
        float(word)
        return True
    except ValueError:
        return False

def is_hex_str(word: str) -> bool:
    try:
        int(word, 16)
        return True
    except ValueError:
        return False

def get_string_list(output):
    "Parses string representation of emacslisp list of strings and returns python list of strings"
    if output == "nil":
        return []
    output = re.findall('"[^"]*"', output)
    output = [x.strip('"') for x in output]
    return output

T = TypeVar('T')

def get_subsets(word_list: [T], subsets=None) -> Set[Tuple[T, ...]]:
    "Get all subsets of a list preserving item ordering."
    if subsets is None:
        subsets = set()
    if not word_list or tuple(word_list) in subsets:
        return subsets
    subsets.add(tuple(word_list))
    for i in range(len(word_list)):
        get_subsets(word_list[0:i] + word_list[i+1:len(word_list)], subsets)
    return subsets

ones_and_teens = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
                  "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
tens = ["", "", "twenty", "thirty", "fourty", "fifty", "sixty", "seventy", "eighty", "ninety"]

def is_number_word(s):
    return s in ones_and_teens or s in tens

def translate_number(digits_string):
    """Translate a string of digits to words describing a series of
numbers between 0-99. So 1050 becomes ten fifty. Necessary because
wav2letter doesn't understand digits directly."""

    num = int(digits_string)
    if num < 0:
         # remove hypen
        return ["negative"] + translate_number(digits_string[1:])
    elif num >= 100:
        # evaluate in pairs, so 1050 becomes "ten fifty"
        return translate_number(digits_string[:2]) + translate_number(digits_string[2:])
    elif num <= 19:
        return [ones_and_teens[num]]
    else:
        result = [tens[num // 10]]
        ones = ones_and_teens[num % 10]
        if ones:
            result += [ones]
        return result

transition_filtered = set()
entropy_filtered = set()

@functools.lru_cache(maxsize=None)
def decompose_word(word: str) -> List[str]:
    "Breakup words that dont have separators, e.g. 'foxbrownhouse' -> ['fox', 'brown', 'house']"
    subwords = []
    for i in range(len(word)):
        for j in range(len(word)-1):
            subword = word[i:j+2]
            if subword.lower() in english_words and len(subword) > 2:
                subwords.append(subword)

    r = []
    if not subwords:
        r = [word]
    else:
        longest_subword = max(subwords, key=lambda x: len(x))
        loc = word.index(longest_subword)
        before = word[:loc]
        after = word[loc+len(longest_subword):]
        if before:
            r.extend(decompose_word(before))
        r.append(longest_subword)
        if after:
            r.extend(decompose_word(after))

    return r

@functools.lru_cache(maxsize=None)
def make_pronouncable(item: str) -> Tuple[str,...]:
    "Transform string into a list of words."
    debug = False
    if debug: log.info(f"item: {item}")
    if debug: log.info(f"item: {item}")
    words = item.translate(delete_punctuation)
    if debug: log.info(f"words1: {words}")
    # delete weird unicode chars
    words = ''.join([c if c in string.printable else ' ' for c in words if c in string.printable])
    if debug: log.info(f"words2: {words}")
    words = words.split()

    # decamelize, but only let dictionary words through
    if debug: log.info(f"words3: {words}")
    possible_words = []
    for word in words:
        possible_words.extend(decamelize(word))
    if debug: log.info(f"possible words: {possible_words}")
    new_words = []
    buffering = []
    for word in possible_words:
        if (word.lower() in english_words and len(word) > 2) or word in words:
#            log.info(f"In dict: {word.lower()}")
            if buffering:
                new_words.append("".join(buffering))
                buffering = []
            new_words.append(word)
        else:
#            log.info(f"Not in dict: {word.lower()}")
            buffering.append(word)
    if buffering:
        new_words.append("".join(buffering))
        buffering = []
    words = new_words

    if debug: log.info(f"words4: {words}")
    if debug: log.info(f"before decompose: {words}")
    new_words = []
    for word in words:
        new_words.extend(decompose_word(word))
    words = new_words
    if debug: log.info(f"after decompose: {words}")

    # If there are too many category transitions in a word, it's
    # probably garbage like a hash. We want to filter these out before
    # we decamelize, because decamelize will turn these into many small
    # words none of which is obviously high entropy.
    if debug: log.info(f"words4.5: {words}")
    before = len(words)
    oldwords = words
    newwords = []
    for word in words:
        score = count_category_transitions(word)/len(word)
        if score >= 0.51:
            if word not in transition_filtered:
                log.info(f"Transition filtered word: {word} Score: {count_category_transitions(word)}/{len(word)}={count_category_transitions(word)/len(word)}")
                transition_filtered.add(word)
            continue
        newwords.append(word)
    words = newwords

    # Even having filtered out words with too many category
    # transitions, we can still have random garbage that stays within
    # a single category, so filter on entropy as well, but with a
    # higher threshold.
    if debug: log.info(f"words4.75: {words}")
    newwords = []
    for word in words:
        if word.lower() not in english_words and compute_average_entropy(word) > 8.5e-7:
            if word not in entropy_filtered:
                log.info(f"Entropy early filtered word: {word} Score: {compute_average_entropy(word)}")
                entropy_filtered.add(word)
            continue
        newwords.append(word)
    words = newwords

    if debug: log.info(f"words5: {words}")
    words = [word.strip() for word in words]
    if debug: log.info(f"words6: {words}")
    words = [word.lower() for word in words]
    if debug: log.info(f"words7: {words}")
    words = [word_substitutions[word] if word in word_substitutions else word for word in words]

    # Even having filtered out words with too many category
    # transitions, we can still have random garbage that stays within
    # a single category, so filter on entropy as well.
    newwords = []
    for word in words:
        if word.lower() not in english_words and compute_average_entropy(word) > 8e-7:
            if word not in entropy_filtered:
                log.info(f"Entropy late filtered word: {word} Score: {compute_average_entropy(word)}")
                entropy_filtered.add(word)
            continue
        newwords.append(word)
    words = newwords


    if debug: log.info(f"words8: {words}")
    words = [" ".join(translate_number(word)) if word.isnumeric() else word for word in words]

    # When we calculate subsets we want numbers to append to most
    # recent word, otherwise number of subsets explodes. So:
    # "foo three five bar four"
    # becomes ["foo three five", "bar four"]
    # Which is way fewer subsets to deal with.
    newwords = []
    streak = 0
    for word in words:
        if is_number_word(word) and newwords and streak < 3:
            newwords[-1] += " " + word
            streak += 1
        else:
            streak = 0
            newwords.append(word)
    words = newwords

    if debug: log.info(f"words9: {words}")
    return tuple(words)

def make_subset_pronunciation_map(item: str) -> Dict[str, str]:
    SUBSET_LIMIT = 8 # prevent subset size explosion for very long strings
    pronunciation = make_pronouncable(item)
    if not pronunciation: # can happen if all words are high entropy
        return {}
    return {" ".join(subset) : item for subset in get_subsets(pronunciation[:SUBSET_LIMIT])}

def get_pronunciation_map(items: [str]) -> Dict[str, Set[str]]:
    """Takes list of items we'd like to dictate and makes them
pronouncable first. Because there might be overlap between
pronouncable subsets, e.g. foo.py and bar.py both have 'py' in common,
pronunciations are mapped to sets."""
#    log.info("==============================================================================")
    values = items
    m = {}
    for item in items:
        pronunciation_map = make_subset_pronunciation_map(item)
        for pronunication, value in pronunciation_map.items():
            if pronunication not in m:
                m[pronunication] = set()
            m[pronunication].add(value)
#    pprint(m)
    return m

def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj

dumped_yet = False

class ListQuery(object):
    def __init__(self, mod: Module, ctx: Context, name: str, cmd: str, interval_ms=1000, allow_subsets=True):
        self.name = name
        self.cmd = cmd
        self.interval_ms = interval_ms
        self.mod = mod
        self.ctx = ctx
        log.info(f"Registering list {name}")
#        self.mod.capture(name, desc=f"All possibilities for {name}")
        self.mod.list(name+"_list", desc=f"List backing all possibilities for {name}")
        self.pronunciation_map = {}
        self.last_choice_map = {}
        self.logging = False
        self.allow_subsets = allow_subsets
        self.size_high_watermark = 0

        # we declare capture on the     modules
        def local_mod_declaration(m) -> str:
            pass
        f = local_mod_declaration
        f.__name__ = name
        f.__doc__ = f"Gets best choice of item for {name}."
        mod.capture(f)

        # then we implement them on the context
        r = f"{{user.{name}_list}}"
        @ctx.capture(f"user.{name}", rule=r)
        def local_capture(m) -> Optional[str]:
            if not m:
                return None
            incoming = " ".join(list(m))
            return incoming

        cron.interval(f"{interval_ms}ms", self._update)

    def _current_choice(self) -> str:
        raise NotImplementedError

    def _update(self):
        output = runEmacsCmd(self.cmd)
        if not output:
            return
        processed = self._post_process(output)
        self._commit(processed)

    def _filter(self, string):
        return (is_float_str(string)
                or is_hex_str(string)
                or sum(c.isalpha() for c in string) < 2
                or string.isnumeric())

    def _post_process(self, data: str) -> Dict[str, Set[str]]:
        strings = get_string_list(data)
        strings = [s for s in strings if not self._filter(s)]
#        for s in strings:
#            log.info(f"{s}: {compute_average_entropy(s)}")
        if self.allow_subsets:
            return get_pronunciation_map(strings)
        al = {}
        for s in strings:
#            log.info(f"Make pronuncable: {s}")
            pronunciation = make_pronouncable(s)
            if pronunciation:
#                log.info(f"pronunciation: {pronunciation}")
                al[" ".join(pronunciation)] = set([s])
        return al

    def dump_mem(self):
        import objgraph
        import time
        import io
        output = io.StringIO()
        objgraph.show_growth(file=output)
        output = output.getvalue()
        if output:
            global dumped_yet
            with open("/tmp/datalog", "a+" if dumped_yet else 'w') as f:
                f.write(f"Time: {time.time()}\n")
                f.write(f"Uploading: {self.name}\n")
                f.write(output)
                dumped_yet = True

    def _commit(self, data: Dict[str, Set[str]]):
        self.pronunciation_map = data
        if self.logging:
            pprint(self.pronunciation_map)
        if len(data) > self.size_high_watermark:
            log.info(f"Loading {self.name} list with length: {len(data.keys())}")
            self.size_high_watermark = len(data)
            with open(f"/tmp/{self.name}_high_watermark", 'w') as f:
                import json
                json.dump(data, f, indent=4, default=serialize_sets)

#        self.dump_mem()
#        log.info("before update")
        self.ctx.lists[f"user.{self.name}_list"] = data.keys()
#        log.info("after update")
#        self.dump_mem()

    def get_choice(self, incoming) -> str:
        return self.get_choice_and_whether_cycling(incoming)[0]

    def get_choice_and_whether_cycling(self, incoming) -> Tuple[str, bool]:
#        log.info("============================================")
#        pprint(incoming)
        if incoming not in self.pronunciation_map:
            return ("", False)

        possibilities = list(self.pronunciation_map[incoming])

        # need to split out subset functionality somehow... snippets
        # are really just exact matching
        if not self.allow_subsets:
            return (possibilities[0], False)

#        pprint(possibilities)
        current = self._current_choice()
        log.info(f"Current choice: {current}")
        choice = None
        cycling = False
        # are we already on a matching option? if so pick the next match.
        if current in possibilities:
            index = possibilities.index(current)
            choice = possibilities[(index+1) % len(possibilities)]
            cycling = True
        # If not, check what we switched to last time. Why is this
        # desirable? Say I have foo.talon, foo.py, and bar.py open. I
        # say "buff py" and I get foo.py, but I wanted bar.py, so I
        # say "buff py" again, and get bar.py. Now I want to toggle
        # back and forth between foo.talon and bar.py. Saying "buff
        # talon" and "buff py" repeatedly will do that, because "buff
        # py" won't cycle to the next python file unless you're
        # already on one.
        if choice is None and incoming in self.last_choice_map and self.last_choice_map[incoming] in possibilities:
            choice = self.last_choice_map[incoming]
        # if we never picked anything, go with the first one
        if choice is None:
            choice = possibilities[0]
        self.last_choice_map[incoming] = choice
        return (choice, cycling)

#log.info(get_subsets([1, 2, 3, 4]))

# good test tokens:
# /py3_import_tests.sh
# VENDOR_PACKAGE_ARCHIVE_FILE=libhugetlbfs-2
# py|sh|bash|png|js|css|json|cfg
# 552|INFO
# create_cc_toolchain_config_info
# drwxr-xr-x
