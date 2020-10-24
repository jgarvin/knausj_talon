destroy window: key(ctrl-alt-x)
restart window manager: key(ctrl-shift-alt-q)
launch emacs: key(ctrl-shift-alt-w)

east:
    key(ctrl-alt-space)

move east:
    key(ctrl-shift-alt-space)

west:
    key(ctrl-alt-backspace)

move west:
    key(ctrl-shift-alt-backspace)

clock: key(ctrl-alt-e)
wise: key(ctrl-alt-h)
move clock: key(ctrl-alt-shift-e)
move wise: key(ctrl-alt-shift-e)
expand: key(ctrl-alt-=)
shrink: key(ctrl-alt-minus)
cycle: key(ctrl-shift-alt-])
master: key(ctrl-alt-enter)
add master: key(ctrl-alt-,)
remove master: key(ctrl-alt-.)
browser: key(ctrl-shift-alt-b)
new terminal: key(ctrl-shift-alt-t)
reflect X: key(ctrl-shift-alt-x)
reflect Y: key(ctrl-shift-alt-y)

desk <user.number_key>:
    k = user.unmap_number(number_key)
    key("ctrl-alt-{k}")
    
move desk <user.number_key>: key("ctrl-shift-alt-{number_key}")

view <user.unmodified_key>: user.emacs_char_cmd("(md-select-window-with-glyph %c)", unmodified_key)