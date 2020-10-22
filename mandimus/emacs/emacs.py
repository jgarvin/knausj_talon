from talon import actions, Module
from user.knausj_talon.mandimus.emacs.connection import runEmacsCmd

def emacsChar(char):
    c = ["?"]
    # most characters don't need escaping, but some do
    if char in " \n\t()\\|;'`\"#.,\a\b\f\r":
        c.append("\\")
    c.append(char)
    return "".join(c)

mod = Module()

@mod.action_class
class Actions:
    def emacs_lisp(lisp: str):
        "Send some emacslisp to emacs to run."
        runEmacsCmd(lisp)

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
