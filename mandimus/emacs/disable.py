from talon import actions, Module, Context, speech_system
import logging as log

mod = Module()
ctx = Context()

def parse_phrase(word_list):
    return " ".join(word.split("\\")[0] for word in word_list)

def on_phrase(j):
    global hist_len
    global history

    try:
        val = parse_phrase(getattr(j["parsed"], "_unmapped", j["phrase"]))
    except:
        val = parse_phrase(j["phrase"])

    if val == "scrumptious quire":
        actions.speech.enable()        

speech_system.register("phrase", on_phrase)

@mod.action_class
class Actions:
    def noop():
        "Do nothing."
        (lambda: False)() # prevent talon from detecting this is a noop
