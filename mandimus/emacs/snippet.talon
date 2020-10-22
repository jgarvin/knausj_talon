os: linux
app: emacs
-

warp <user.unmodified_key>: user.emacs_char_cmd('(md-sn-find-slot %c)', unmodified_key)
blank: user.emacs_lisp('(md-sn-next-slot)')
make blank: user.emacs_lisp('(md-sn-drop-slot)')
make <user.snippet>: user.emacs_insert_snippet(snippet)
