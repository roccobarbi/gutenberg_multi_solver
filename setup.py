import argparse
import json
import os
import queue
import shutil
import requests
import gutenberg_list_builder
import text_stripper
import time
from word_descriptor import WordDescriptor
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
    unique_words = 0
    total_occurrences = 0
    with open(outfile_name, "w") as outfile:
        outfile.write("word,books,occurrences")
        for word in words.keys():
            outfile.write("\n{},{},{}".format(words[word].word, words[word].sources, words[word].occurrences))
            unique_words += 1
            total_occurrences += words[word].occurrences
    return unique_words, total_occurrences


def words_from_book(book_text=""):
    words = {}
    for word in book_text.split():
        word = word.lower()
        if word not in words.keys():
            words[word] = WordDescriptor(word, 1, 1)
        else:
            words[word].occurrences += 1
    return words


def merge_word_dict_into(target, source):
    for word in source.keys():
        if word in target.keys():
            target[word].merge(source[word])
        else:
            target[word] = source[word]
    return target


def remove_pattern_dir():
    module_dir, module_file = os.path.split(__file__)
    patterns_dir = os.path.join(module_dir, "patterns")
    if os.path.exists(patterns_dir) and os.path.isdir(patterns_dir):
        shutil.rmtree(patterns_dir)


def build_pattern_map(wordlist, source_threshold, occurrences_threshold):
    patterns = {}
    i = 0
    for word_name in wordlist.keys():
        word = wordlist[word_name]
        if word.sources >= source_threshold and word.occurrences >= occurrences_threshold:
            i += 1
            if len(word) not in patterns.keys():
                patterns[len(word)] = {}
            if word.unique not in patterns[len(word)]:
                patterns[len(word)][word.unique] = {}
            if word.pattern not in patterns[len(word)][word.unique]:
                patterns[len(word)][word.unique][word.pattern] = []
            patterns[len(word)][word.unique][word.pattern].append(word.dictionary())
    print("[+] Mapped {} patterns with at least {} sources and {} occurrences.".format(
        i,
        source_threshold,
        occurrences_threshold
    ))
    return patterns


def build_pattern_map_directories(patterns):
    module_dir, module_file = os.path.split(__file__)
    patterns_dir = os.path.join(module_dir, "patterns")
    if not os.path.exists(patterns_dir):
        os.mkdir(patterns_dir)
    for word_length in patterns.keys():
        word_length_dir = os.path.join(patterns_dir, str(word_length))
        os.mkdir(os.path.join(word_length_dir))


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
    argument_parser.add_argument("-u", "--urls", type=str, default=None, help="Optional file with list of urls")
    argument_parser.add_argument("-w", "--wordlist", type=str, default=None, help="Optional file with a wordlist")
    argument_parser.add_argument("-s", "--sources", type=int, default=0, help="Optional file with a wordlist")
    argument_parser.add_argument("-c", "--count", type=int, default=0, help="Optional file with a wordlist")
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
    if args.wordlist is not None:
        print("[+] Reading wordlist from {}.".format(args.wordlist))
        try:
            with open(args.wordlist, "r") as infile:
                i = 0
                for line in infile:
                    if i > 0:
                        line = line.strip().split(",")
                        words[line[0]] = WordDescriptor(line[0], int(line[1]), int(line[2]))
                    i += 1
                print("[+] {} words read from {}.".format(i, args.wordlist))
        except:
            print("[!] Error reading wordlist!")
    else:
        if args.urls is None:
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
            print("\n[!] Error while counting and merging words: {}!".format(e))
        print("[+] Writing results.")
        unique, occurrences = write_output(outfile_name, words)
        print("[+] Classified {} occurrences of {} unique words from {} books.".format(occurrences, unique, books_count))
    print("[+] Cleaning up any previous word pattern files and directories")
    remove_pattern_dir()
    print("[+] Building wordlist by length and pattern.")
    patterns = build_pattern_map(words, args.sources, args.count)
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
