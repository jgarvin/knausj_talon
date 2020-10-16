os: linux
app: emacs
-

# replace w/ real folder cmd later
folder: key(ctrl-t ctrl-j)

command: key(alt-x)

exit debug: key(ctrl-t x a)

#toggle emacs debug

go to line: key(alt-g alt-g)

#new frame

#minibuffer

list buffs: key(ctrl-t ctrl-b ctrl-t o)

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
recent files: key(ctrl-c ctrl-e)
sudo open file: key(ctrl-c o s)

man page: user.minibuffer("man")
find file: user.minibuffer("find-name-dired")

switch buff: key(ctrl-t b)
destroy buff: key(ctrl-t k enter)

# show home folder
# show temp folder
# show root folder

start irc: user.minibuffer("irc-maybe")
stop irc: user.minibuffer("stop-irc")
# stop irc
# toggle tail mode
list packages: user.minibuffer("list-packages")

get status: key(ctrl-t g)

# open terminal
# open temp

magnify: key(ctrl-t ctrl-+)
demagnify: key(ctrl-t ctrl--)

visual line mode: user.minibuffer("visual-line-mode")

# set indent

# toggle namespace indent

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

# axe
super axe: key(ctrl-g)
eval: key(ctrl-t ctrl-e)
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

# copy
# cut
# mark
# comment

copy: key(alt-w)
cut: key(ctrl-w)
mark: key(ctrl-space)
comment: key(alt-;)

kill: key(ctrl-k)

# squeeze

paste: key(ctrl-y)
rotate: key(alt-y)

select all: key(ctrl-home ctrl-space ctrl-end)
fish: key(alt-space)
undo: key(ctrl-/)
redo: key(alt-/)

# shift right
# shift left

align regexp: user.minibuffer("align-regexp")
# indent

capitalize: key(alt-c)
bigger: key(alt-u)
smaller: key(alt-l)

# jump
# jump char

snap: key(ctrl-u ctrl-space)
big snap: key(ctrl-t ctrl-space)

insert character: key(ctrl-t 8 enter)

open this: key(ctrl-enter)

shell command: user.minibuffer("etc-shell-command")
# insert pth
# insert base name
# insert buffer name
# insert name without extension
# insert directory
# insert extension
# insert username

switch previous: key(ctrl-t ctrl-left)
switch next: key(ctrl-t ctrl-right)

search: key(ctrl-s)
lurch: key(ctrl-r)
swoop: key(alt-i)
show kill ring: key(ctrl-shift-y)

submit: key(ctrl-c ctrl-c)
discard: key(ctrl-c ctrl-k)

# view

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