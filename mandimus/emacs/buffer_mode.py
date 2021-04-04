#!/usr/bin/env python
# -*- coding: utf-8 -*-

from user.knausj_talon.mandimus.emacs.connection import runEmacsCmd
from typing import Callable, List
from talon import ui, cron
import time
import logging as log

REFRESH_MS=1000

_subscriptions = []

def _get_emacs_list(x):
    x = x.strip("()")
    return x.split()

class BufferModeSubscription(object):
    def __init__(self, f: Callable[[List[str]], None]):
        self.f = f
        _subscriptions.append(self)

    def __del__(self):
        self.cancel()

    def cancel(self):
        if self.f is not None:
            _subscriptions.remove(self)
            self.f = None

_major_modes = None
_last_call = time.time()
def update_buffer_mode(win=None):
    global _major_modes, _subscriptions, _last_call
    new_time = time.time()
    time_since_last_call_ms = (new_time - _last_call)*1000
    if time_since_last_call_ms < REFRESH_MS*.95:
        return
    log.info(f"Last time: {int(time_since_last_call_ms)}ms")
    modes = runEmacsCmd("(md-get-all-modes)")
    if modes == "": # can't get modes, not connected to emacs
        return
    modes = _get_emacs_list(modes)
    if _major_modes != modes:
        log.info(f"Emacs mode switch: {modes}")
        _major_modes = modes
        for sub in _subscriptions:
            sub.f(_major_modes)
    _last_call = new_time

def subscribe_buffer_mode(f: Callable[[List[str]], None]) -> BufferModeSubscription:
    global _major_modes
    x = BufferModeSubscription(f)
    if _major_modes is not None:
        x.f(_major_modes)

cron.interval(f"{REFRESH_MS}ms", update_buffer_mode)
ui.register('win_focus', update_buffer_mode)
ui.register('win_title', update_buffer_mode)
