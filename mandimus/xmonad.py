from talon import Module

unmap = {
    1: '!',
    2: '@',
    3: '#',
    4: '$',
    5: '%',
    6: '^',
    7: '&',
    8: '*',
    9: '(',
    0: ')',
}

mod = Module()

@mod.action_class
class Actions:
    def unmap_number(n: str) -> str:
        "Translates a number back to punctuation key."
        return unmap[int(n)]