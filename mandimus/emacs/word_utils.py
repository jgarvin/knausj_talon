import logging as log
import re, string

UPPER = 0
LOWER = 1
OTHER = 2

def category(c):
    if c in string.ascii_uppercase:
        return UPPER
    elif c in string.ascii_lowercase:
        return LOWER
    else:
        return OTHER

def decamelize(word):
    cat = None
    wordList = []
    buildingWord = []

    # temporary hack, need better parsing
    mixedCase = len({category(c) for c in word}) > 1

    # think this originally did more splitting, but in talon we always remove special letters first...
    if not mixedCase:
        return [word]

    for i, c in enumerate(word):
        newCategory = category(c)
        isLast = i == len(word)-1
        if (cat and cat != newCategory) or (newCategory == UPPER and cat == UPPER and mixedCase):
            wordList.append(''.join(buildingWord))
            buildingWord = []
        if isLast:
            buildingWord.append(c)
            newWord = ''.join(buildingWord)
            if newWord == newWord.upper():
                wordList.extend(newWord)
            else:
                wordList.append(newWord)
            buildingWord = []
        cat = newCategory
        buildingWord.append(c)

    # do a final pass to make sure we split on special characters
    # that occur after a run of capital letters
    finalWordList = []
    for w in wordList:
        newWords = re.split(r'([^a-zA-Z])', w)
        newWords = [a for a in newWords if a]
        finalWordList.extend(newWords)
    return finalWordList

def splitFlatten(slist, s=' '):
    x = []
    for i in slist:
        x.extend(i.split(s))
    return x

def deepEmpty(x):
    if not isinstance(x, collections.Iterable):
        return True
    elif not x:
        return True
    elif isinstance(x, dict):
        return all([deepEmpty(i) for i in x.values()])
    elif type(x) == str or type(x) == unicode:
        # this has to be its own case because python
        # doesn't distinguish strings from characters
        return len(x) == 0
    else:
        return all([deepEmpty(i) for i in x])


punc2Words = {
    "*" : ["star", "asterisk"],
    "#" : ["sharp"],
}

englishWords = set()
with open("/usr/share/dict/american-english") as f:
#with open("/home/jgarvin/mandimus/american-english") as f:
    for w in f.readlines():
        # strip punctuation because there's a bunch of weird
        # apostrophes and other things.
        word = "".join(c for c in w if c not in string.punctuation)
        word = word.lower()
        englishWords.update(set(re.findall("[a-z]+", word)))


normalConsonantBlends = {
    "bl",
    "br",
    "pr",
    "dr",
    "fl",
    "cl",
    "gl",
    "sl",
    "cr",
    "pl",
    "fr",
    "gr",
    "tr",
    "sc",
    "sk",
    "st",
    "sw",
    "sn",
    "sm",
    "wh",
    "str",
    "sh",
    "th",
    "tw",
    "wr",
    "sch",
    "shr",
    "sph",
    "scr",
    "spl",
    "spr",
    "squ",
    "thr",
    # my additions below
    "omb", # otherwise comb becomes comoob
    "cc",
    "ff",
    "gg",
    "ll",
    "mm",
    "nn",
    "pp",
    "ss",
    "tt",
    "ck",
}

consonants = { 'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n',
               'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z' }

# y isn't always a vowel but when it doesn't it still
# doesn't usually create a pronunciation problem
vowels = { 'a', 'e', 'i', 'o', 'u', 'y' }

l33tTranslation = {
    '0' : 'o',
    '1' : 'l',
    '3' : 'e',
    '4' : 'a',
    '7' : 't',
}



def deL33t(w):
    return ''.join(l33tTranslation[c] if c in l33tTranslation else c for c in w)

def fixBadConsonantPairs(w):
    """put 'oo' between unnatural consonant blends to make them
    pronouncable, so wb -> woob"""
    word = []
    i = 0
    while i < len(w):
        #log.info(word)
        if i+2 < len(w) and w[i:i+3] in normalConsonantBlends:
            #log.info('path A')
            word.extend(w[i:i+2])
            i += 2
            continue
        if i+1 < len(w):
            if w[i:i+2] in normalConsonantBlends:
                #log.info('path B')
                word.extend(w[i])
                i += 1
                continue
            a, b = w[i:i+2]
            #log.info((a, b))
            if a in consonants and b in consonants:
                #log.info('path C')
                word.extend([a, 'o', 'o', b])
                i += 2
                continue
        #log.info('path D')
        word.extend(w[i])
        i += 1
    return ''.join(word)

# TODO: maybe give translate a better default
def extractWords(wordstr, splitters={' ', '\n', '\t'} | set(string.punctuation), translate={},
                 useDict=False, removeLeetSpeak=False, detectBadConsonantPairs=False,
                 filterUnicode=True):
    """Split a string into a list using multiple delimeters, and optionally
    translating some characters to one or more words. Also lowercase everything."""
    splitters = splitters - set(translate.keys())
    all_words = []
    word = []
    strlen = len(wordstr)

    if filterUnicode:
        wordstr = ''.join([c for c in wordstr if c in string.printable])

    def finish(w):
        if removeLeetSpeak:
            w = deL33t(w)

        # change 'camelCase' to ['camel', 'case']
        new_words = [i.lower() for i in deCamelize(''.join(w))]
        # you have to capitalize single letters for Dragon to recognize them as words
        new_words = [i if len(i) > 1 else i.upper() for i in new_words]

        toReplace = {}
        if detectBadConsonantPairs:
            for n in new_words:
                fixed = fixBadConsonantPairs(n)
                if fixed != n:
                    toReplace[n] = fixed

        # change 'blastgreenhouse' to ['blast', 'green', 'house']
        if useDict:
            for word in new_words:
                new_subwords = set()
                for i in range(len(word)):
                    for j in range(len(word)-1):
                        subword = word[i:j+2]
                        if subword in englishWords and len(subword) > 2:
                            new_subwords.add(subword)

                # take the top 3 longest subwords, otherwise you get a
                # a ton of fragments
                new_subwords = list(new_subwords)
                new_subwords.sort(key=lambda x: len(x))
                new_subwords = new_subwords[:3]
                all_words.extend(new_subwords)

        # we do this after because we don't want the dictionary
        # stuff to run on the imaginary words we made by fixing
        # bad consonant pairs
        for k, v in toReplace.items():
            try:
                new_words.remove(k)
            except ValueError:
                pass
            new_words.append(v)

        all_words.extend(new_words)

    for c in wordstr:
        if c in splitters:
            if word:
                finish(word)
                word = []
        elif c in translate:
            if word:
                finish(word)
                word = []
            all_words.extend(translate[c])
        else:
            word.append(c)
    if word:
        finish(word)
    return all_words

if __name__ == "__main__":
    print(extractWords("wgreenhouse", useDict=True))
    print(extractWords("ijp", detectBadConsonantPairs=True))
    print(extractWords("twb", detectBadConsonantPairs=True))
    print(extractWords("t4ngo", removeLeetSpeak=True))
    print(extractWords("BFF"))
    print()
    print(fixBadConsonantPairs("twb"))
    print(fixBadConsonantPairs("ijp"))
    print(fixBadConsonantPairs("throw"))
