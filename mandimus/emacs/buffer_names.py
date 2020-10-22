#!/usr/bin/env python
# -*- coding: utf-8 -*-

from talon import Module, Context, actions
from typing import Optional
from user.knausj_talon.mandimus.emacs.connection import runEmacsCmd
from user.knausj_talon.mandimus.emacs.query import ListQuery
import logging as log

mod = Module()
ctx = Context()

class BufferNames(ListQuery):
    def __init__(self, mod, ctx, name, query):
        self.base_query = query
        ListQuery.__init__(self, mod, ctx, name, f"(md-get-buffer-names {query})")

    def _current_choice(self) -> str:
        return runEmacsCmd("(buffer-name (current-buffer))").strip().strip('"')

    def switch_no_choice(self):
        runEmacsCmd("(md-switch-to-next-buffer-in-list %s)" % self.base_query, queryOnly=False)

    def switch_buffer(self, incoming: Optional[str] = None):
        log.info("***********************************")
        if incoming is None:
            self.switch_no_choice()
            return
        buffer_name = self.get_choice(incoming)
        runEmacsCmd(f"(switch-to-buffer \"{buffer_name}\")")

class FolderNames(BufferNames):
    def __init__(self):
        BufferNames.__init__(self, mod, ctx, "folder_name", "(md-get-buffers-in-modes 'dired-mode)")

    def switch_no_choice(self):
        runEmacsCmd("(md-folder-switch)", queryOnly=False)

FOLDER_NAMES = FolderNames()

class ShellNames(BufferNames):
    def __init__(self):
        BufferNames.__init__(self, mod, ctx, "shell_name", "(md-get-buffers-in-modes 'shell-mode)")

    def switch_no_choice(self):
        actions.key("ctrl-z")

SHELL_NAMES = ShellNames()

class EshellNames(BufferNames):
    def __init__(self):
        BufferNames.__init__(self, mod, ctx, "eshell_name", "(md-get-buffers-in-modes 'eshell-mode)")
#        self.logging = True

    def switch_no_choice(self):
        actions.key("ctrl-c")
        actions.key("z")

ESHELL_NAMES = EshellNames()

class ChannelNames(BufferNames):
    def __init__(self):
        BufferNames.__init__(self, mod, ctx, "channel_name", "(md-get-buffers-in-modes 'erc-mode)")
#        self.logging = True

CHANNEL_NAMES = ChannelNames()

class SpecialNames(BufferNames):
    def __init__(self):
        BufferNames.__init__(self, mod, ctx, "special_name", "(md-get-special-buffers)")
#        self.logging = True

SPECIAL_NAMES = SpecialNames()

_bufferQueryTable = [
    FOLDER_NAMES,
    SHELL_NAMES,
    ESHELL_NAMES,
    CHANNEL_NAMES,
    SPECIAL_NAMES,
]

_appendCmd = "(append %s)" % " ".join([e.base_query for e in _bufferQueryTable])
_allBuffQuery = "(md-all-buffers-except %s)" % _appendCmd

class GeneralBufferNames(BufferNames):
    def __init__(self):
        BufferNames.__init__(self, mod, ctx, "buffer_name", _allBuffQuery)
#        self.logging = True

GENERAL_BUFFER_NAMES = GeneralBufferNames()

@mod.action_class
class Actions:
    def switch_buffer(buffer_name: Optional[str]):
        "Switch to buffer."
        GENERAL_BUFFER_NAMES.switch_buffer(buffer_name)

    def switch_folder(buffer_name: Optional[str]):
        "Switch to folder."
        FOLDER_NAMES.switch_buffer(buffer_name)

    def switch_shell(buffer_name: Optional[str]):
        "Switch to shell."
        SHELL_NAMES.switch_buffer(buffer_name)

    def switch_eshell(buffer_name: Optional[str]):
        "Switch to eshell."
        ESHELL_NAMES.switch_buffer(buffer_name)

    def switch_channel(buffer_name: Optional[str]):
        "Switch to channel."
        CHANNEL_NAMES.switch_buffer(buffer_name)

    def switch_special(buffer_name: Optional[str]):
        "Switch to special."
        SPECIAL_NAMES.switch_buffer(buffer_name)
        