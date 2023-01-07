class WordDescriptor:
    """
    Class to describe a word and its properties, relative to a wordlist compiled from the internet.

    word: the word
    pattern: the normalized pattern of the word
    unique: the number of unique letters in the word
    sources: the number of sources (books, web pages...) where the word was fount at least once
    occurrences: the total number of times that the word was encountered

    The pattern can be used to look up words that match a certain pattern (e.g. people = abcadb).
    The number of unique letters can be used to aide in the classification of patterns.
    The number of sources can be used to assess how common the word is (vs. a made up or technical name).
    The number of occurrences can be used to assess how frequent the word is in its context.

    Sources and occurrences are meant to reduce the length and complexity of word lists where common words are more
    likely to be useful.
    """
    def __init__(self,
                 word="",
                 sources=0,
                 occurrences=0):
        self.word = word
        self.sources = sources
        self.occurrences = occurrences
        self.unique = 0
        self.pattern = ""
        char_map = {}
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        for char in self.word:
            if char in ['\'', '-']:
                self.pattern += char
            else:
                if char not in char_map.keys():
                    char_map[char] = self.unique
                    self.unique += 1
                self.pattern += alphabet[char_map[char]]

    def __repr__(self):
        return "WordDescriptor(word={}, sources={}, occurrences={})".format(
            self.word,
            self.sources,
            self.occurrences
        )

    def __str__(self):
        return "Word: {}, Pattern: {}".format(self.word, self.pattern)

    def __len__(self):
        return len(self.word)

    def dictionary(self):
        return {
            "word": self.word,
            "pattern": self.pattern,
            "unique": self.unique,
            "sources": self.sources,
            "occurrences": self.occurrences
        }

    def merge(self, other):
        if not isinstance(other, WordDescriptor):
            raise TypeError("other must be an instance of WordDescriptor")
        if other.word != self.word:
            raise TypeError("other must reference the same word: {} is not {}".format(other.word, self.word))
        self.sources += other.sources
        self.occurrences += other.occurrences
