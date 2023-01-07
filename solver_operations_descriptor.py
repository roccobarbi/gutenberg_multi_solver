class SolverOperationsDescriptor:
    def __init__(self,
                 words=[],
                 alphabet="",
                 common={},
                 unique={},
                 couples=[]):
        self.words = words
        self.alphabet = alphabet
        self.common = common
        self.unique = unique
        self.couples = couples

    def __repr__(self):
        return "WordDescriptor(words={}, alphabet={}, common={}, unique={}, couples={})".format(
            self.words,
            self.alphabet,
            self.common,
            self.unique,
            self.couples
        )

    def __str__(self):
        return self.__repr__()
