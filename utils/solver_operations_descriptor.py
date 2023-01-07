class SolverOperationsDescriptor:
    def __init__(self,
                 words=None,
                 verbose=False):
        self.words = words
        if verbose:
            print("[+] Words listed for analysis: {}.".format(words))
        self.alphabet = ""
        for word in words:
            for character in word:
                if character not in self.alphabet:
                    self.alphabet += character
        self.alphabet = ''.join(sorted(self.alphabet))
        if verbose:
            print("[+] Cipher alphabet compiled: {}.".format(self.alphabet))
        self.common = {}
        self.unique = {}
        if verbose:
            print("[+] Common and unique letters analysed.")
        self.couples = []
        if verbose:
            print("[+] Couples ordered for analysis.")
            print("[+] Order of operations laid out.")

    def __repr__(self):
        return "WordDescriptor(words={})".format(self.words)

    def __str__(self):
        return self.__repr__()
