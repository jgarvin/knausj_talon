# -1 because we are repeating, so the initial command counts as one
#<user.ordinals>: core.repeat_command(ordinals-1)
<number_small>: core.repeat_command(number_small-1)
(rep | rip | rup | rap | ep): core.repeat_partial_phrase(1)
(rep | rip | rup | rap | ep) <number_small>: core.repeat_partial_phrase(number_small)

# pretty much never intentionally start a phrase with a number, ignore!
^<number_small>: core.cancel_phrase__unstable()
