#!/usr/bin/env python
# -*- coding: utf-8 -*-

from talon import Module, Context, cron
from typing import Union, List, Dict, TypeVar, Set, Tuple, Optional
from user.knausj_talon.mandimus.emacs.connection import runEmacsCmd
from user.knausj_talon.mandimus.emacs.word_utils import decamelize
from user.knausj_talon.code.keys import alphabet
import logging as log
import re
import string
from copy import copy
import functools
from pprint import pprint

word_substitutions = {
    "py" : "pie"
}
word_substitutions.update({v:k for k,v in alphabet.items()})

delete_punctuation = "".maketrans(string.punctuation, " "*len(string.punctuation))

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

@functools.lru_cache(maxsize=None)
def make_pronouncable(item: str) -> Tuple[str,...]:
    "Transform string into a list of words."
    debug = False
    if debug: log.info(f"item: {item}")
    words = item.translate(delete_punctuation)
    if debug: log.info(f"words1: {words}")
    # delete weird unicode chars
    words = ''.join([c if c in string.printable else ' ' for c in words if c in string.printable])
    if debug: log.info(f"words2: {words}")
    words = words.split()
    if debug: log.info(f"words3: {words}")
    words = [decamelize(word) for word in words]
    if debug: log.info(f"words4: {words}")
    new_words = []
    for word in words:
        new_words.extend(word)
    words = new_words
    if debug: log.info(f"words5: {words}")
    words = [word.strip() for word in words]
    if debug: log.info(f"words6: {words}")
    words = [word.lower() for word in words]
    if debug: log.info(f"words7: {words}")
    words = [word_substitutions[word] if word in word_substitutions else word for word in words]
    if debug: log.info(f"words8: {words}")
    words = [" ".join(translate_number(word)) if word.isnumeric() else word for word in words]
    if debug: log.info(f"words9: {words}")
    return tuple(words)

def make_subset_pronunciation_map(item: str) -> Dict[str, str]:
    SUBSET_LIMIT = 8 # prevent subset size explosion for very long strings
    return {" ".join(subset) : item for subset in get_subsets(make_pronouncable(item)[:SUBSET_LIMIT])}

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

class ListQuery(object):
    def __init__(self, mod: Module, ctx: Context, name: str, cmd: str, interval_ms=1000, allow_subsets=True, capture_required=False):
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
        if not capture_required:
            r = "[" + r + "]"
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

    def _post_process(self, data: str) -> Dict[str, Set[str]]:
        strings = get_string_list(data)
        if self.allow_subsets:
            return get_pronunciation_map(strings)
        return {" ".join(make_pronouncable(s)):{s} for s in strings}

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
        self.ctx.lists[f"user.{self.name}_list"] = list(data.keys())

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