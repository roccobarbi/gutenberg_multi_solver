class MatchRecord:
    def __init__(self,
                 words=[],
                 cipher=[],
                 plain=[],
                 key={}):
        self.words = words
        self.cipher = cipher
        self.plain = plain
        self.key = key

    def __repr__(self):
        return "MatchRecord(words={}, cipher={}, plain={}, key={})".format(
            self.words,
            self.cipher,
            self.plain,
            self.key
        )

    def __str__(self):
        return "MatchRecord(cipher={}, plain={})".format(
            self.cipher,
            self.plain
        )

    def clone(self):
        words = []
        cipher = []
        plain = []
        key = {}
        for item in self.words:
            words.append(item)
        for item in self.cipher:
            cipher.append(item)
        for item in self.plain:
            plain.append(item)
        for pin in self.key.keys():
            key[pin] = self.key[pin]
        return MatchRecord(words, cipher, plain, key)
