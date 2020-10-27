#!/usr/bin/env python
# -*- coding: utf-8 -*-

from talon import speech_system, Module, Context

mod = Module()
ctx = Context()

@mod.action_class
class Actions:
    def dump_talon_debug_info():
        "Dump debugging information for aegis."
        blob = speech_system.engine.engine.cfg_blobs['talon_main']
        with open('/tmp/talon_blob_dump', 'wb') as f:
            f.write(blob)
