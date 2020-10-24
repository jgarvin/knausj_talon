#!/usr/bin/env python
# -*- coding: utf-8 -*-

from talon import Module, Context, actions
from typing import Optional
from user.knausj_talon.mandimus.emacs.connection import runEmacsCmd
from user.knausj_talon.mandimus.emacs.query import ListQuery
import logging as log

mod = Module()
ctx = Context()

class WordNames(ListQuery):
    def __init__(self, mod, ctx):
        ListQuery.__init__(self, mod, ctx, "word_name", f"md-global-word-cache", capture_required=True)
#        self.logging = True

    def _current_choice(self) -> str:
        return runEmacsCmd("(substring-no-properties (let ((sym (thing-at-point 'word))) (if sym sym \"\")))").strip().strip('"')

    def insert_word(self, incoming: Optional[str] = None):
        if incoming is None:
            self.switch_no_choice()
            return
        choice, cycling = self.get_choice_and_whether_cycling(incoming)
        if cycling:
            actions.user.emacs_cut("word")
        actions.insert(choice)

WORD_NAMES = WordNames(mod, ctx)

@mod.action_class
class Actions:
    def emacs_insert_word(buffer_name: Optional[str]):
        "Insert nearby word into buffer."
        WORD_NAMES.insert_word(buffer_name)




# insert insert names
