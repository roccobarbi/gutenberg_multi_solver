# TODO: split words, for each word strip whitespaces and stops
# TODO: for each word, only pass long words or whitelisted short words
# TODO: on everything that remains, only pass words that contain whitelisted symbols
import re


class TextStripper:
    def __init__(self, text=""):
        self.text = text

    def __repr__(self):
        return 'TextStripper(text=%s)' % self.text

    def __str__(self):
        return self.__repr__()

    def strip_all(self, text=""):
        if text == "":
            text = self.text
        text = self.strip_html_tags(text)
        text = self.strip_punctuation(text)
        text = self.strip_non_words(text)
        text = self.strip_short_words(text)
        return text

    def strip_plaintext(self, text="", min_length=0):
        if text == "":
            text = self.text
        text = self.strip_punctuation(text)
        text = self.strip_non_words(text)
        if not min_length > 0:
            text = self.strip_short_words(text, min_length)
        return text

    def strip_html_tags(self, text=""):
        if text == "":
            text = self.text
        temp_text = []
        tag_name = ''
        tag_open = False
        reading_name = False
        style_tag_open = False
        script_tag_open = False
        for character in text:
            if tag_open:
                if character == ">":
                    if reading_name and tag_name != "/a":  # sometimes <a>name</a>'s may be used
                        temp_text.append(" ")  # Safety to avoid linking different words together
                    tag_open = False
                    if reading_name:
                        reading_name = False
                        if tag_name == "style":
                            style_tag_open = True
                        elif tag_name == "/style":
                            style_tag_open = False
                        elif tag_name == "script":
                            script_tag_open = True
                        elif tag_name == "/script":
                            script_tag_open = False
                elif reading_name:
                    if character == " ":
                        reading_name = False
                        if tag_name == "style":
                            style_tag_open = True
                        elif tag_name == "/style":
                            style_tag_open = False
                        elif tag_name == "script":
                            script_tag_open = True
                        elif tag_name == "/script":
                            script_tag_open = False
                    else:
                        tag_name += character
            else:
                if character == "<":
                    tag_open = True
                    reading_name = True
                    tag_name = ''
                elif not (style_tag_open or script_tag_open):
                    temp_text.append(character)
        return ''.join(temp_text)

    def strip_punctuation(self, text=""):
        if text == "":
            text = self.text
        punctuation = ",.?;:!\"()"
        temp_text = []
        for character in text:
            if character in punctuation:
                temp_text.append(" ")
            else:
                temp_text.append(character)
        return "".join(temp_text)

    def strip_non_words(self, text=""):
        if text == "":
            text = self.text
        blacklist = re.compile('^.*[^a-zA-Z-\'].*$')
        text = text.split()
        temp_text = []
        for word in text:
            if blacklist.match(word) is None:
                temp_text.append(word.strip("'-"))  # Leading and trailing ' and - are removed
        return temp_text

    def strip_short_words(self, text="", min_length=0):
        if text == "":
            text = self.text
        temp_text = []
        for word in text:
            if len(word) >= min_length:
                temp_text.append(word)
        return " ".join(temp_text)

    def strip_multiple_signs(self, text="", strict=False):
        # When more than a consecutive non-alphabetic sign is encountered, either ignore the whole entry (strict=True),
        # or split the entry in two words (strict=False).
        pass
