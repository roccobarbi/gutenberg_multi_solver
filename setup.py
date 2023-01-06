import argparse
import json
import os
import queue
import shutil
import requests
import gutenberg_list_builder
import text_stripper
import time
from multiprocessing import Process, Queue


def download_and_parse_books(q_in, q_out, num):
    while not q_in.empty():
        book = q_in.get()
        try:
            r = requests.get(book)
            s = text_stripper.TextStripper(r.text)
            q_out.put(s.strip_plaintext())
        except Exception as e:
            print("[!] Process {} could not load {}!".format(num, book))
    return


def write_output(outfile_name, words):
    unique = 0
    occurrences = 0
    with open(outfile_name, "w") as outfile:
        outfile.write("word,books,occurrences")
        for word in words.keys():
            outfile.write("\n{},{},{}".format(words[word]["word"], words[word]["books"], words[word]["count"]))
            unique += 1
            occurrences += words[word]["count"]
    return unique, occurrences


def words_from_book(book_text=""):
    words = {}
    for word in book_text.split():
        word = word.lower()
        if word not in words.keys():
            words[word] = {"word": word, "books": 1, "count": 1}
        else:
            words[word]["count"] += 1
    return words


def merge_word_dict_into(target, source):
    for word in source.keys():
        if word in target.keys():
            target[word]["books"] += 1
            target[word]["count"] += source[word]["count"]
        else:
            target[word] = source[word]
    return target


def remove_pattern_dir():
    module_dir, module_file = os.path.split(__file__)
    patterns_dir = os.path.join(module_dir, "patterns")
    if os.path.exists(patterns_dir) and os.path.isdir(patterns_dir):
        shutil.rmtree(patterns_dir)


def build_word_pattern(word):
    """Given a word descriptor, calculate the word pattern and the number of unique character is has."""
    pattern = ""
    unique = 0
    char_map = {}
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for char in word["word"]:
        if char in ['\'', '-']:
            pattern += char
        else:
            if char not in char_map.keys():
                char_map[char] = unique
                unique += 1
            pattern += alphabet[char_map[char]]
    return {
        "pattern": pattern,
        "word": word["word"],
        "unique": unique,
        "books": word["books"],
        "occurrences": word["occurrences"]
    }


def build_pattern_map(wordlist):
    patterns = {}
    for word in wordlist:
        descriptor = build_word_pattern(word)
        if len(word["word"]) not in patterns.keys():
            patterns[len(word["word"])] = {}
        if descriptor["unique"] not in patterns[len(word["word"])]:
            patterns[len(word["word"])][descriptor["unique"]] = {}
        if descriptor["pattern"] not in patterns[len(word["word"])][descriptor["unique"]]:
            patterns[len(word["word"])][descriptor["unique"]][descriptor["pattern"]] = []
        patterns[len(word["word"])][descriptor["unique"]][descriptor["pattern"]].append(descriptor)
    return patterns


def build_pattern_map_directories(patterns):
    module_dir, module_file = os.path.split(__file__)
    patterns_dir = os.path.join(module_dir, "patterns")
    if not os.path.exists(patterns_dir):
        os.mkdir(patterns_dir)
    for word_length in patterns.keys():
        os.mkdir(os.path.join(patterns_dir, str(word_length)))


def save_pattern_map(patterns):
    module_dir, module_file = os.path.split(__file__)
    patterns_dir = os.path.join(module_dir, "patterns")
    for word_length in patterns.keys():
        word_length_dir = os.path.join(patterns_dir, str(word_length))
        for word_unique in patterns[word_length].keys():
            with open(os.path.join(word_length_dir, str(word_unique) + ".json"), "w", encoding="utf-8") as outfile:
                json.dump(patterns[word_length][word_unique], outfile, ensure_ascii=False, indent=4)


def main():
    time_start = time.time()
    print("[+] Setup started.")
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-p", "--processes", type=int, default=1, help="Number of max processes (default 1).")
    argument_parser.add_argument("-o", "--out", type=str, default=None, help="Optional name of the output file.")
    argument_parser.add_argument("-l", "--language", type=str, default="english", help="Optional language.")
    argument_parser.add_argument("-u", "--urls", type=str, default="", help="Optional file with list of urls")
    args = argument_parser.parse_args()
    if args.out is None:
        outfile_name = "out_gutenberg_" + str(int(time.time())) + ".txt"
    else:
        outfile_name = args.out
    books_queue = Queue()
    words_queue = Queue()
    processes = []
    words = {}
    print("[+] Preliminary operations done.")
    if args.urls == "":
        print("[+] Building a list of Project Gutenberg books.")
        list_builder = gutenberg_list_builder.GutenbergListBuilder()
        books_list = list_builder.build()
        print("[+] {} books listed from Project Gutenberg.".format(len(books_list)))
    else:
        print("[+] Reading URL list from {}.".format(args.urls))
        with open(args.urls, "r") as infile:
            books_list = json.load(infile)
    books_count = len(books_list)
    print("[+] Enqueueing books.", end="", flush=True)
    for book in books_list:
        if book["language"].lower() == "english":
            books_queue.put(book["book"])
            print(".", end="", flush=True)
    print("\n[+] Books enqueued.")
    print("[+] Spawning download processes.")
    for i in range(args.processes):
        proc = Process(target=download_and_parse_books, args=(books_queue, words_queue, i))
        processes.append(proc)
        proc.start()
    print("[+] Download processes spawned.")
    print("[+] Counting and merging words.", end="", flush=True)
    try:
        while True:
            book_words = words_from_book(words_queue.get(block=True, timeout=10))
            words = merge_word_dict_into(words, book_words)
            print(".", end="", flush=True)
    except queue.Empty:
        print("\n[!] Queue empty!")
    except Exception as e:
        print("\n[!] Error while counting and merging words! {}".format(e))
    print("[+] Writing results.")
    unique, occurrences = write_output(outfile_name, words)
    print("[+] Classified {} occurrences of {} unique words from {} books.".format(occurrences, unique, books_count))
    print("[+] Cleaning up any previous word list files and directories")
    remove_pattern_dir()
    print("[+] Building word list by length and pattern.")
    patterns = build_pattern_map(words)
    print("[+] Building the directory structure.")
    build_pattern_map_directories(patterns)
    print("[+] Saving the patterns to disk.")
    save_pattern_map(patterns)
    print("[+] Word list built.")
    print("[+] Closing processes.")
    for proc in processes:
        proc.join()
    print("[+] Processes closed.")
    time_end = time.time()
    print("[+] Setup finished in {} seconds.".format(time_end - time_start))


if __name__ == "__main__":
    main()
