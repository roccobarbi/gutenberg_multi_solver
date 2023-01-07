def extract_alphabet_from_words(words):
    alphabet = ""
    for word in words:
        for character in word:
            if character not in alphabet:
                alphabet += character
    return ''.join(sorted(alphabet))


def extract_common_letters_from_words(words, alphabet):
    common = {}
    for char in alphabet:
        char_descriptor = []
        for i in range(len(words)):
            try:
                position = (i, words[i].index(char))
                char_descriptor.append(position)
            except ValueError:
                pass
        if len(char_descriptor) > 1:
            common[char] = char_descriptor
    return common


def extract_unique_letters_from_descriptor(alphabet, common, words):
    unique = {}
    for char in alphabet:
        if char not in common.keys():
            for i in range(len(words)):
                try:
                    position = (i, words[i].index(char))
                    unique[char] = position
                except ValueError:
                    pass
    return unique


def define_order_of_operations(words):
    order = []
    for i in range(len(words)):
        alpha = ""
        for char in words[i]:
            if char not in alpha:
                alpha += char
        for j in range(i + 1, len(words)):
            common = 0
            for char in alpha:
                if char in words[j]:
                    common += 1
            order.append((i, j, common))
    order.sort(key=lambda a: a[2], reverse=True)
    added = []
    output = []
    for couple in order:
        if couple[0] in added and couple[1] in added:
            pass
        else:
            output.append(couple)
            if couple[0] not in added:
                added.append(couple[0])
            if couple[1] not in added:
                added.append(couple[1])
    return output


class SolverOperationsDescriptor:
    def __init__(self,
                 words=None,
                 verbose=False):
        self.words = words
        if verbose:
            print("[+] Words listed for analysis: {}.".format(words))
        self.alphabet = extract_alphabet_from_words(self.words)
        if verbose:
            print("[+] Cipher alphabet compiled: {}.".format(self.alphabet))
        self.common = extract_common_letters_from_words(self.words, self.alphabet)
        if verbose:
            print("[+] Common letters analysed: {}".format(str(self.common)))
        self.unique = extract_unique_letters_from_descriptor(self.alphabet, self.common, self.words)
        if verbose:
            print("[+] Unique letters analysed: {}".format(str(self.unique)))
        if len(words) == 2:
            self.couples = [(0, 1, len(self.common))]
        else:
            self.couples = define_order_of_operations(self.words)
        if verbose:
            print("[+] Couples ordered for analysis: {}".format(self.couples))
            print("[+] Order of operations laid out.")

    def __repr__(self):
        return "WordDescriptor(words={})".format(self.words)

    def __str__(self):
        return self.__repr__()
