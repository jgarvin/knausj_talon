from talon import actions, Module, Context
from typing import Optional
import logging as log
from user.knausj_talon.mandimus.emacs.connection import runEmacsCmd

def emacsChar(char):
    c = ["?"]
    if char == "space":
        char = " "
    # most characters don't need escaping, but some do
    if char in " \n\t()\\|;'`\"#.,\a\b\f\r":
        c.append("\\")
    c.append(char)
    return "".join(c)

mod = Module()
ctx = Context()

ctx.matches = """
os: linux
app: emacs
"""

@mod.capture
def emacs_unit(m) -> str:
    "Returns name of unit that can be cut/copy/pasted, e.g. word, symbol, line, filename, etc."

@ctx.capture("user.emacs_unit", rule="[(word | symbol | line | filename | paragraph | buffer)]")
def emacs_unit_impl(m) -> Optional[str]:
    return " ".join(list(m))

@ctx.action_class("main")
class emacs_main_overrides:
    def insert(text: str):
        # t t = capital check, space check
        runEmacsCmd(f"(md-insert-text \"{text}\" t t)")

@mod.action_class
class Actions:
    def emacs_lisp(lisp: str):
        "Send some emacslisp to emacs to run."
        runEmacsCmd(lisp)

    def emacs_insert_no_space(text: str):
        "Insert text without automatically inserting spaces."
        # nil nil = capital check, space check
        runEmacsCmd(f"(md-insert-text \"{text}\" nil nil)")

    def emacs_query(lisp: str):
        "Send some emacslisp to emacs to run without simulating a keypress."
        return runEmacsCmd(lisp, queryOnly=True)

    def emacs_char_cmd(lisp: str, char: str):
        "Run emacs command using given character."
        char = emacsChar(char)
        runEmacsCmd(lisp.replace("%c", char))

    def minibuffer(command: str):
        "Execute a command in the minibuffer."
        actions.key("ctrl-t")
        actions.key("ctrl-m")
        actions.insert(command)
        actions.key("enter")

    def emacs_insert_string(stringReturningElisp: str):
        "Run emacslisp and insert resulting text into the buffer."
        data = "(md-insert-text %s nil nil)" % stringReturningElisp
        runEmacsCmd(data)

    def emacs_mark(unit: Optional[str]):
        "Mark a unit of text in emacs."
        if unit is None or unit == "":
            actions.key("ctrl-space")
            return
        runEmacsCmd(f"(md-mark-thing '{unit})")

    def emacs_copy(unit: Optional[str]):
        "Copy a unit of text in emacs."
        if unit is not None and unit != "":
            Actions.emacs_mark(unit)
        actions.key("alt-w")

    def emacs_cut(unit: Optional[str]):
        "Cut a unit of text in emacs."
        if unit is not None and unit != "":
            Actions.emacs_mark(unit)
        actions.key("ctrl-w")

    def emacs_comment(unit: Optional[str]):
        "Comment a unit of text in emacs."
        if unit is not None and unit != "":
            Actions.emacs_mark(unit)
        actions.key("alt-;")

    def emacs_goto_next(text: str):
        "Go to next instance of text."
        runEmacsCmd(f"(md-go-to-next \"{text}\")")

    def emacs_goto_previous(text: str):
        "Go to previous instance of text."
        runEmacsCmd(f"(md-go-to-previous \"{text}\")")
