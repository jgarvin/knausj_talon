#!/usr/bin/env python
# -*- coding: utf-8 -*-

from talon import Module, Context, cron
from typing import Union, List, Dict, TypeVar, Set, Tuple
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

@functools.lru_cache(maxsize=None)
def make_pronouncable(item: str) -> Tuple[str,...]:
    "Transform string into a list of words."
    words = item.translate(delete_punctuation)
    # delete weird unicode chars
    words = ''.join([c if c in string.printable else ' ' for c in words if c in string.printable])
    words = words.split()
    words = [decamelize(word) for word in words]
    new_words = []
    for word in words:
        new_words.extend(word)
    words = new_words
    words = [word.strip() for word in words]
    words = [word.lower() for word in words]
    words = [word_substitutions[word] if word in word_substitutions else word for word in words]
    return tuple(words)

def make_subset_pronunciation_map(item: str) -> Dict[str, str]:
    return {" ".join(subset) : item for subset in get_subsets(make_pronouncable(item))}

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

class ListQuery(object):
    def __init__(self, mod: Module, ctx: Context, name: str, cmd: str, interval_ms=1000):
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

        # we declare capture on the modules
        def local_mod_declaration(m) -> str:
            pass
        f = local_mod_declaration
        f.__name__ = name
        f.__doc__ = f"Gets best choice of item for {name}."
        mod.capture(f)

        # then we implement them on the context
        @ctx.capture(f"user.{name}", rule=f"{{user.{name}_list}}")
        def local_capture(m) -> Set[str]:
            incoming = " ".join(list(m))
            return incoming

        cron.interval(f"{interval_ms}ms", self._update)

    def _current_choice(self) -> str:
        raise NotImplemented()

    def _update(self):
        output = runEmacsCmd(self.cmd)
        if not output:
            return
        processed = self._post_process(output)
        self._commit(processed)

    def _post_process(self, data: str) -> Union[List[str], Dict[str, str]]:
        return get_pronunciation_map(get_string_list(data))

    def _commit(self, data: Dict[str, Set[str]]):
        self.pronunciation_map = data
        if self.logging:
            pprint(self.pronunciation_map)
        self.ctx.lists[f"user.{self.name}_list"] = data.keys()

    def get_choice(self, incoming):
#        log.info("============================================")
#        pprint(incoming)
        if incoming not in self.pronunciation_map:
            return None
        possibilities = list(self.pronunciation_map[incoming])
#        pprint(possibilities)
        current = self._current_choice()
        choice = None
        # are we already on a matching option? if so pick the next match.
        if current in possibilities:
            index = possibilities.index(current)
            choice = possibilities[(index+1) % len(possibilities)]
        # If not, check what we switched to last time. Why is this
        # desirable? Say I have foo.talon, foo.py, and bar.py open. I
        # say "buff py" and I get foo.py, but I wanted bar.py, so I
        # say "buff py" again, and get bar.py. Now I want to toggle
        # back and forth between foo.talon and bar.py. Saying "buff
        # talon" and "buff py" repeatedly will do that, because "buff
        # py" won't cycle to the next python file unless you're
        # already on one.
        if choice is None and incoming in self.last_choice_map:
            choice = self.last_choice_map[incoming]
        # if we never picked anything, go with the first one
        if choice is None:
            choice = possibilities[0]
        self.last_choice_map[incoming] = choice
        return choice

#log.info(get_subsets([1, 2, 3, 4]))