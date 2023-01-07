import argparse
import time

from utils.solver_operations_descriptor import SolverOperationsDescriptor
from utils.match_record import MatchRecord


def extract_common_unique_cipher_letters(words):
    return {}, {}


def main():
    time_start = time.time()
    print("[+] Program started.")
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-a", "--aca", action="store_true", help="Flag if ACA rules should be applied.")
    argument_parser.add_argument("words", nargs="*", help="The words that you're looking to decipher.")
    args = argument_parser.parse_args()
    print("[+] Starting preliminary operations.")
    operations_layout = SolverOperationsDescriptor(args.words, verbose=True)
    print("[+] Preliminary operations completed.")
    time_end = time.time()
    print("[+] Execution completed in {:.4} seconds.".format(time_end - time_start))


if __name__ == "__main__":
    main()
