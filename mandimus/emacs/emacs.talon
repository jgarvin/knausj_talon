os: linux
app: emacs
-

# TODO: make mode dependent
dired copy: key(ctrl-c alt-w)
dired cut: key(ctrl-c ctrl-w)
dired paste: key(ctrl-c ctrl-y)
dired create: key(+)

# replace w/ real folder cmd later
folder: key(ctrl-t ctrl-j)

command: key(alt-x)

exit debug: key(ctrl-t x a)

toggle emacs debug: user.emacs_lisp("(toggle-debug-on-error)")

go to line: key(alt-g alt-g)

new frame: key(ctrl-t 5 2)

minibuffer: user.emacs_lisp("(md-select-minibuffer)")

list buffs: key(ctrl-t ctrl-b ctrl-t o)

key {user.emacs_language_keywords}: insert(emacs_language_keywords)
go key {user.emacs_language_keywords}: user.emacs_goto_next(emacs_language_keywords)
come key {user.emacs_language_keywords}: user.emacs_goto_previous(emacs_language_keywords)

switch project: key(ctrl-c p p)
root folder: key(ctrl-c p d)
project search: key(ctrl-c p s g)
directory search: key(ctrl-c p s d)
project source search: key(ctrl-c p s s)
occur: key(ctrl-c p o)
project replace: key(ctrl-c p r)
project file: key(ctrl-c p f)
project kill: key(ctrl-c p k)
project root: key(ctrl-c p D)
invalidate projectile cache: key(ctrl-c p i)

oops: key(alt-g n)
spoo: key(alt-g p)
toggle trace: key(ctrl-c ctrl-f)

plain open file: key(ctrl-t ctrl-f)
alternate file: key(ctrl-t ctrl-v)
recent files: user.emacs_lisp("(recentf-open-files)")
sudo open file: key(ctrl-c o s)

man page: user.minibuffer("man")
find file: user.minibuffer("find-name-dired")

switch buff: key(ctrl-t b)
destroy buff: key(ctrl-t k enter)

show home folder: user.emacs_lisp("(find-file \"~\")")
show temp folder: user.emacs_lisp("(find-file \"/tmp\")")
show root folder: user.emacs_lisp("(find-file \"/\")")

start irc: user.minibuffer("irc-maybe")
stop irc: user.minibuffer("stop-irc")
toggle tail mode: user.emacs_lisp("(auto-revert-tail-mode)")
list packages: user.minibuffer("list-packages")

get status: key(ctrl-t g)

open terminal: user.emacs_lisp("(etc-start-or-open-terminal)")
open temporary: user.emacs_lisp("(md-create-temp-file \"temp\")")
open temp: user.emacs_lisp("(md-create-temp-file \"temp\")")
open tramp: key(ctrl-c s t)

magnify: key(ctrl-t ctrl-+)
demagnify: key(ctrl-t ctrl--)

visual line mode: user.minibuffer("visual-line-mode")

set indent <number_small>: user.emacs_lisp("(etc-set-indent-preference {number_small})")

toggle namespace indent: user.emacs_lisp("(etc-toggle-namespace-indent)")

toggle read only: key(ctrl-t ctrl-q)

help function: key(ctrl-h f)
help language: key(ctrl-h g)
help variable: key(ctrl-h v)
help key: key(ctrl-h k)
help mode: key(ctrl-h m)
help docks: key(ctrl-h d)
help news: key(ctrl-h n)
help info: key(ctrl-h i)
help syntax: key(ctrl-h s)
help bindings: key(ctrl-h s)
inspect character: key(ctrl-u ctrl-t =)

cancel: user.emacs_query("(setq unread-command-events (append unread-command-events (list ?\\C-g)))")
super cancel: key(ctrl-g)
evaluate: key(ctrl-t ctrl-e)
start macro: key(F3)
mack: key(F4)
other: key(ctrl-t o)
collapse: key(ctrl-])

replace: key(alt-%)
regex replace: key(ctrl-%)
center: key(ctrl-l)

exchange: key(ctrl-t ctrl-t)
select: key(ctrl-=)
contract: key(alt-=)

[<user.emacs_unit>] copy: user.emacs_copy(emacs_unit or "")
[<user.emacs_unit>] cut: user.emacs_cut(emacs_unit or "")
[<user.emacs_unit>] (mark | marks): user.emacs_mark(emacs_unit or "")
[<user.emacs_unit>] comment: user.emacs_comment(emacs_unit or "")
[<user.emacs_unit>] indent: user.emacs_indent(emacs_unit or "")
rectangle: key(ctrl-t space)

# only here to override generic_editor definitions
copy: user.emacs_copy("")
cut: user.emacs_cut("")

kill: key(ctrl-k)

squeeze: user.emacs_lisp("(cycle-spacing)")

paste: key(ctrl-y)
rotate: key(alt-y)

select all: key(ctrl-home ctrl-space ctrl-end)
fish: key(alt-space)
undo: key(ctrl-/)
redo: key(alt-/)

shift right: user.emacs_lisp("(call-interactively 'python-indent-shift-right)")
shift left: user.emacs_lisp("(call-interactively 'python-indent-shift-left)")

align regexp: user.minibuffer("align-regexp")

capitalize: key(alt-c)
bigger: key(alt-u)
smaller: key(alt-l)

jump <user.unmodified_key>:
    key(alt-enter)
    key(unmodified_key)

jump char <user.unmodified_key>:
    key(ctrl-u alt-enter)
    key(unmodified_key)

snap: key(ctrl-u ctrl-space)
big snap: key(ctrl-t ctrl-space)

insert character: key(ctrl-t 8 enter)

open this: key(ctrl-enter)

shell command: user.minibuffer("etc-shell-command")
insert path: user.emacs_insert_string("(buffer-file-name)")
insert base name: user.emacs_insert_string("(file-name-base (buffer-file-name))")
insert buffer name: user.emacs_insert_string("(buffer-name)")
insert name without extension: user.emacs_insert_string("(file-name-sans-extension (buffer-file-name))")
insert directory: user.emacs_insert_string("(file-name-directory (buffer-file-name))")
insert extension: user.emacs_insert_string("(file-name-extension (buffer-file-name))")
insert username: user.emacs_insert_string('(user-login-name)')

switch previous: key(ctrl-t ctrl-left)
switch next: key(ctrl-t ctrl-right)

search: key(ctrl-s)
lurch: key(ctrl-r)
swoop: key(alt-i)
show kill ring: key(ctrl-shift-y)

submit: key(ctrl-c ctrl-c)
discard: key(ctrl-c ctrl-k)

view <user.unmodified_key>:
    key(alt-d)
    key(unmodified_key)

hide block: key(ctrl-c h)
unfold: key(ctrl-c u)
show block: key(ctrl-c f)
hide all: key(ctrl-c H)
show all: key(ctrl-c U)
toggle: key(alt-t)

prior: key(alt-p)
future: key(alt-n)
read email: key(ctrl-c e)
compose email: key(ctrl-x m)
jabber roster: key(ctrl-t ctrl-j ctrl-r)
fill paragraph: key(alt-q)

maggot find file: key(ctrl-c m h)
maggot show origin master: key(ctrl-c m o)

last change: key(ctrl-.)
next change: key(ctrl-,)

language rename: key(super-l r r)
language action: key(super-l a a)
language completion: key(ctrl-c .)
language expand: key(ctrl-c e)

inquisition:
    user.minibuffer("magit-blame")
    key(b)

fasten <user.text>: user.emacs_insert_no_space(text)

prior: key(alt-p)
future: key(alt-n)
history: key(alt-r)
interrupt: key(ctrl-c ctrl-c)
exit: key(ctrl-d)
prompt up: key(ctrl-c ctrl-p)
prompt down: key(ctrl-c ctrl-n)
