os: linux
app: emacs
-

top side: key(alt-<)
bottom: key(alt->)

over: user.emacs_lisp("(forward-symbol 1)")
under: user.emacs_lisp("(forward-symbol -1)")

gruff: key(alt-{)
graph: key(alt-})

go <user.unmodified_key>: user.emacs_char_cmd("(md-move-up-to-char 1 %c)", unmodified_key)
doog <user.unmodified_key>: user.emacs_char_cmd("(md-move-up-to-char -1 %c)", unmodified_key)

#function: key(ctrl-alt-a)

snug: user.emacs_lisp("(md-find-indentation-change 1 '>)")
guns: user.emacs_lisp("(md-find-indentation-change -1 '>)")
loosen: user.emacs_lisp("(md-find-indentation-change 1 '<)")
nesool: user.emacs_lisp("(md-find-indentation-change -1 '<)")

store <user.unmodified_key>: user.emacs_char_cmd("(copy-to-register %c (region-beginning) (region-end))", unmodified_key)
insert <user.unmodified_key>: user.emacs_char_cmd("(insert-register %c)", unmodified_key)
bookmark <user.unmodified_key>: user.emacs_char_cmd("(point-to-register %c)", unmodified_key)
load <user.unmodified_key>: user.emacs_char_cmd("(jump-to-register %c)", unmodified_key)

previous: user.emacs_lisp("(md-get-previous-instance-of-symbol)")
next: user.emacs_lisp("(md-get-next-instance-of-symbol)")

line <user.unmodified_key>$: user.emacs_char_cmd("(md-find-line-starting-with-char 1 %c)", unmodified_key)
nile <user.unmodified_key>$: user.emacs_char_cmd("(md-find-line-starting-with-char -1 %c)", unmodified_key)
sim <user.unmodified_key>: user.emacs_char_cmd("(md-move-up-to-symbol-starting-with-char nil %c)", unmodified_key)
miss <user.unmodified_key>: user.emacs_char_cmd("(md-move-up-to-symbol-starting-with-char t %c)", unmodified_key)

lookup: key(alt-.)
references: key(alt-,)
