#defines the various mode commands
mode: all
-
# welcome back:
#     user.mouse_wake()
#     user.history_enable()
#     user.talon_mode()
# sleep all:
#     user.switcher_hide_running()
#     user.history_disable()
#     user.homophones_hide()
#     user.help_hide()
#     user.mouse_sleep()
#     speech.disable()
#     user.engine_sleep()
snore: speech.disable()
(hello|hey) beautiful: speech.disable()
(hello|hey) gorgeous: speech.disable()
(hello|hey) love muffin: speech.disable()
(hello|hey) love bucket: speech.disable()
(hello|hey) love of my life: speech.disable()
(hello|hey) my love: speech.disable()
#^surely this is too long to trigger by accident$: speech.enable()
^scrumptious: user.noop()
quire$: user.noop()
# begin: these commands are really for windows & mac with Dragon.
#dragon mode: user.dragon_mode()
#talon mode: user.talon_mode()
# end: these commands are really for windows & mac on Dragon.
#^dictation mode$:
#    mode.disable("sleep")
#    mode.disable("command")
#    mode.enable("dictation")
#    user.code_clear_language_mode()
#    mode.disable("user.gdb")
#^command mode$:
#    mode.disable("sleep")
#    mode.disable("dictation")
#    mode.enable("command")
