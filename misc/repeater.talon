# -1 because we are repeating, so the initial command counts as one
#<user.ordinals>: core.repeat_command(ordinals-1)
<number_small>: core.repeat_command(number_small-1)
rep: core.repeat_command(1)
rep <number_small>: core.repeat_command(number_small)
