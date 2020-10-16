from talon import Module, actions

mod = Module()



@mod.action_class
class Actions:
    def emacslisp(lisp: str):
        "Send some emacslisp to emacs to run."
        pass

    def minibuffer(command: str):
        "Execute a command in the minibuffer."
        actions.key("ctrl-t")
        actions.key("ctrl-m")
        actions.insert(command)
        actions.key("enter")

