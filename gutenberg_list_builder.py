# TODO: generalize it to allow lists from different sources

import json
import requests
import time

BASE_URL = "https://gutenberg.org/files/{}/{}-0.txt"


class GutenbergListBuilder:
    def __init__(self,
                 text="",
                 unknown_threshold=100,
                 file_name="list_gutenberg_files_{}.txt".format(str(int(time.time())))):
        self.text = text
        self.unknown_threshold = unknown_threshold
        self.file_name = file_name
        self.books = []

    def __repr__(self):
        return 'TextStripper(text=%s)' % self.text

    def __str__(self):
        return self.__repr__()

    def build(self):
        unknown = 0
        count = 0
        if not self.books:
            while unknown < self.unknown_threshold:
                book = BASE_URL.format(count, count)
                try:
                    if requests.head(book).status_code == 200:
                        text = requests.get(book).text
                        start = text.index("*** START OF THE PROJECT GUTENBERG EBOOK") + 40
                        start += text[start:].index("***") + 3
                        end = text.index("*** END")
                        language_s = text.index("Language:") + 9
                        language_e = text.index("\n", language_s)
                        title_s = text.index("Title:") + 6
                        title_e = text.index("\n", title_s)
                        book_descriptor = {
                            "book": book,
                            "start": start,
                            "end": end,
                            "language": text[language_s:language_e].strip(),
                            "title": text[title_s:title_e].strip()
                        }
                        self.books.append(book_descriptor)
                        unknown = 0
                    else:
                        unknown += 1
                except:
                    unknown += 1
                count += 1
        with open(self.file_name, "w") as outfile:
            outfile.write(json.dumps(self.books))
        return self.books
