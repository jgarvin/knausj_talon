#!/usr/bin/env python
# -*- coding: utf-8 -*-

from talon import Module, Context, actions
from typing import Optional
from user.knausj_talon.mandimus.emacs.connection import runEmacsCmd
from user.knausj_talon.mandimus.emacs.query import ListQuery
import logging as log
from pprint import pprint

mod = Module()
ctx = Context()

class Snippets(ListQuery):
    def __init__(self):
        ListQuery.__init__(self, mod, ctx, "snippet", "(md-get-snippet-names)", allow_subsets=False)

SNIPPETS = Snippets()

@mod.action_class
class Actions:
    def emacs_insert_snippet(snippet_name: str):
        "Insert emacs snippet."
        snippet = SNIPPETS.get_choice(snippet_name)
        runEmacsCmd(f"(md-insert-snippet \"{snippet}\")")
