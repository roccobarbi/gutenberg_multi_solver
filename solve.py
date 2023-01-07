import argparse
import json
import os
import sys
import time

from utils.solver_operations_descriptor import SolverOperationsDescriptor
from utils.match_record import MatchRecord
from utils.word_descriptor import generate_pattern_from_any_word


def lookup_pattern(word, aca):
    output = []
    module_dir, module_file = os.path.split(__file__)
    patterns_dir = os.path.join(module_dir, "patterns")
    pattern, unique = generate_pattern_from_any_word(word)
    length_dir = os.path.join(patterns_dir, str(len(word)))
    map_file = os.path.join(length_dir, str(unique) + ".json")
    if not os.path.exists(length_dir) or not os.path.isdir(length_dir):
        print("[!] Error: patterns not initialised at this location! Please run setup.py, then try again.")
        sys.exit(1)
    if not os.path.exists(map_file) or not os.path.isfile(map_file):
        print("[!] Error: patterns not initialised at this location! Please run setup.py, then try again.")
        sys.exit(1)
    with open(map_file, "r") as infile:
        pattern_map = json.load(infile)
    if pattern in pattern_map.keys():
        for item in pattern_map[pattern]:
            if not aca or not has_aca_illegal_letters(item["word"], word):
                output.append(item["word"])
    if len(output) == 0:
        print("[!] Error: {} has no candidates! Try running setup.py with fewer restrictions.".format(word))
        sys.exit(1)
    return output


def has_aca_illegal_letters(candidate, word):
    for i in range(len(word)):
        if word[i] == candidate[i]:
            return True
    return False


def kickstart_first_word(operations, words, candidates, verbose):
    first_word_index = operations.couples[0][0]
    word = words[first_word_index]
    if verbose:
        print("[+] First word: {}".format(word))
    current_matches = []
    for candidate in candidates[words[first_word_index]]:
        key = {}
        for char_index in range(len(word)):
            if word[char_index] not in key.keys():
                key[word[char_index]] = candidate[char_index]
        current_matches.append(MatchRecord(
            [first_word_index],
            [word],
            [candidate],
            key
        ))
    return current_matches


def generate_bucket_keys(known_letters, new_element):
    bucket_keys = []
    for char in known_letters:
        if char in new_element:
            bucket_keys.append(char)
    return bucket_keys


def main():
    time_start = time.time()
    print("[+] Program started.")
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-a", "--aca", action="store_true", help="Flag if ACA rules should be applied.")
    argument_parser.add_argument("-v", "--verbose", action="store_true", help="Flag to have a more verbose output.")
    argument_parser.add_argument("words", nargs="*", help="2 or more words that you're trying to decipher.")
    args = argument_parser.parse_args()
    print("[+] Starting preliminary operations.")
    if len(args.words) < 2:
        print("[!] Error: 2 or more words should be passed to this program!")
        sys.exit(1)
    operations_layout = SolverOperationsDescriptor(args.words, verbose=args.verbose)
    print("[+] Retrieving candidates for each word.")
    candidates = {}
    for word in args.words:
        candidates[word] = lookup_pattern(word, args.aca)
        if args.verbose:
            print("[+] Retrieved {} candidates for {}.".format(len(candidates[word]), word))
    print("[+] Candidates retrieved.")
    print("[+] Preliminary operations completed.")
    print("[+] Creating first match record")
    current_matches = kickstart_first_word(operations_layout, args.words, candidates, args.verbose)
    if args.verbose:
        print("[+] Created {} match records for the first word.".format(len(current_matches)))
    print("[+] First match record created, starting comparisons.")
    comparison_counter = 1
    for comparison in operations_layout.couples:
        print("[+] Running comparison {}.".format(comparison_counter))
        if comparison[0] not in current_matches[0].words:
            new_element = comparison[0]
        else:
            new_element = comparison[1]
        if args.verbose:
            print("[+] Adding {} to the comparison".format(args.words[new_element]))
        bucket_keys = generate_bucket_keys(current_matches[0].key.keys(), args.words[new_element])
        if args.verbose:
            print("[+] Bucket keys: {}".format(bucket_keys))
        source_buckets = {}
        if args.verbose:
            print("[+] Moving current matches to source buckets.")
        for match in current_matches:
            bucket = ""
            for pin in bucket_keys:
                bucket += match.key[pin]
            if bucket not in source_buckets.keys():
                source_buckets[bucket] = []
            source_buckets[bucket].append(match)
        if args.verbose:
            print("[+] Current matches moved to source buckets.")
        if args.verbose:
            print("[+] Comparing candidates for {}.".format(args.words[new_element]))
        current_matches = []
        for candidate in candidates[args.words[new_element]]:
            bucket = ""
            for pin in bucket_keys:
                bucket += candidate[args.words[new_element].index(pin)]
            if bucket in source_buckets.keys():
                unique = []
                for char in candidate:
                    if char not in bucket and char not in unique:
                        unique.append(char)
                for match in source_buckets[bucket]:
                    good_match = True
                    for char in unique:
                        if char in match.key.keys():
                            good_match = False
                    if good_match:
                        new_match = match.clone()
                        new_match.words.append(new_element)
                        new_match.cipher.append(args.words[new_element])
                        new_match.plain.append(candidate)
                        for char in unique:
                            char_pos = candidate.index(char)
                            new_match.key[args.words[new_element][char_pos]] = char
                        current_matches.append(new_match)
        if args.verbose:
            print("[+] Candidates for {} compared, {} matches found.".format(
                args.words[new_element],
                len(current_matches))
            )
        if len(current_matches) == 0:
            print("[!] No matches found! Try running setup.py with fewer restrictions.")
            sys.exit(1)
        print("[+] Comparison {} complete.".format(comparison_counter))
        comparison_counter += 1
    print("[+] All comparisons completed: {} matches found.".format(len(current_matches)))
    order = []
    for i in range(len(current_matches[0].words)):
        order.append(i)
    for i in range(len(current_matches[0].words)):
        order[current_matches[0].words[i]] = i
    for match in current_matches:
        print("-------------")
        cipher = []
        plain = []
        for i in order:
            cipher.append(match.cipher[i])
            plain.append(match.plain[i])
        print(cipher)
        print(plain)
    print("-------------")
    time_end = time.time()
    print("[+] Execution completed: {} matches found in {:.4} seconds.".format(
        len(current_matches),
        time_end - time_start)
    )


if __name__ == "__main__":
    main()
