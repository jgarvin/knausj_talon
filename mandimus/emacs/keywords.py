#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from user.knausj_talon.mandimus.emacs.buffer_mode import subscribe_buffer_mode
from talon import Module, Context, resource
import logging as log

mod = Module()
ctx = Context()

mod.list("emacs_language_keywords", desc="Language keywords for major mode of active buffer.")

keyword_files = {
    "c-mode" : "cpp_keywords.json",
    "c++-mode" : "cpp_keywords.json",
    "python-mode" : "python_keywords.json",
    "emacs-lisp-mode" : "emacs_lisp_keywords.json",
    "shell-mode" : "shell_keywords.json",
    "sh-mode" : "shell_keywords.json",
    "rust-mode" : "rust_keywords.json",
}

keywords = {}

from pprint import pprint
pprint(keyword_files)
for mode, filename in keyword_files.items():
    mode_keywords = {}
    print(mode)
    print(filename)
    with resource.open(filename, 'r') as f:
        data = json.load(f)
        log.info(f"Loaded keywords for mode: {mode}")
        for entry in data:
            if isinstance(entry, str):
                mode_keywords[entry] = entry
            elif isinstance(entry, list):
                assert(len(entry) == 2)
                mode_keywords[entry[1]] = entry[0]
    keywords[mode] = mode_keywords

def switch_keywords(modes: [str]):
    active_set = {}
    for mode in modes:
        if mode in keywords:
            active_set.update(keywords[mode])
#    log.info("setting active keywords")
#    from pprint import pprint
#    pprint(active_set)
    ctx.lists["user.emacs_language_keywords"] = active_set

_buffer_mode_subscription = subscribe_buffer_mode(switch_keywords)
