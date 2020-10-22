#!/usr/bin/env python
# -*- coding: utf-8 -*-

from talon import Module, Context, actions
from typing import Optional
from user.knausj_talon.mandimus.emacs.connection import runEmacsCmd
from user.knausj_talon.mandimus.emacs.query import ListQuery
import logging as log

mod = Module()
ctx = Context()

class TokenNames(ListQuery):
    def __init__(self, mod, ctx):
        ListQuery.__init__(self, mod, ctx, "token_name", f"md-global-symbol-cache", capture_required=True)
#        self.logging = True

    def _current_choice(self) -> str:
        return runEmacsCmd("(substring-no-properties (let ((sym (thing-at-point 'symbol))) (if sym sym \"\")))").strip().strip('"')

    def insert_token(self, incoming: Optional[str] = None):
        log.info("***********************************")
        if incoming is None:
            self.switch_no_choice()
            return
        choice, cycling = self.get_choice_and_whether_cycling(incoming)
        if cycling:
            actions.key("ctrl-w")
        actions.insert(choice)

TOKEN_NAMES = TokenNames(mod, ctx)

@mod.action_class
class Actions:
    def emacs_insert_token(buffer_name: Optional[str]):
        "Insert nearby token into buffer."
        TOKEN_NAMES.insert_token(buffer_name)

