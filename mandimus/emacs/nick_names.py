#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from talon import Module, Context, actions
from typing import Optional
from user.knausj_talon.mandimus.emacs.connection import runEmacsCmd
from user.knausj_talon.mandimus.emacs.query import ListQuery
import logging as log

mod = Module()
ctx = Context()

class NickNames(ListQuery):
    def __init__(self, mod, ctx,):
        ListQuery.__init__(self, mod, ctx, "nick_name", "md-active-erc-nicknames")

    def _current_choice(self) -> str:
        return runEmacsCmd("(thing-at-point 'symbol)").strip().strip('"')

    def insert_nickname(self, incoming: Optional[str] = None):
        log.info("***********************************")
        if incoming is None:
            return
        nickname = self.get_choice(incoming)
        actions.user.emacs_insert_string(f"\"{nickname}\"")

NICK_NAMES = NickNames(mod, ctx)

@mod.action_class
class Actions:
    def insert_nickname(nickname: Optional[str]):
        "Insert nickname into buffer."
        NICK_NAMES.insert_nickname(nickname)
