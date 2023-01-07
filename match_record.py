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
        return "WordDescriptor(words={}, cipher={}, plain={}, key={})".format(
            self.words,
            self.cipher,
            self.plain,
            self.key
        )

    def __str__(self):
        return "WordDescriptor(cipher={}, plain={})".format(
            self.cipher,
            self.plain
        )
