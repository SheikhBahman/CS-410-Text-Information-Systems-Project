#!/usr/bin/env python
"""
Evaluation scripts for English Lexical Normalisation shared task in W-NUT 2015.
"""


import sys
import argparse
import operator
try:
    import ujson as json
except ImportError:
    import json


class NonCanonical():

    def __init__(self, canonical=''):
        self.canonical = canonical
        self.count = 0
        self.candidates = []


def evaluate(pred_file, oracle_file):
    pred_list = json.load(open(pred_file))
    oracle_list = json.load(open(oracle_file))
    non_canonicals = dict()

    correct_norm = 0.0
    total_norm = 0.0
    total_nsw = 0.0
    for pred, oracle in zip(pred_list, oracle_list):
        try:
            assert(pred["tid"] == oracle["tid"])
            input_tokens = pred["input"]
            pred_tokens = pred["output"]
            oracle_tokens = oracle["output"]
            sent_length = len(input_tokens)
            for i in range(sent_length):
                token = input_tokens[i].lower()
                prediction = pred_tokens[i].lower()
                truth = oracle_tokens[i].lower()
                if prediction != token and truth == prediction and truth.strip():
                    correct_norm += 1
                if truth != token and truth.strip():
                    total_nsw += 1
                if prediction != token and prediction.strip():
                    total_norm += 1

                if prediction != truth:
                    if not token in non_canonicals.keys():
                        non_canonicals[token] = NonCanonical(truth)
                    non_canonicals[token].count += 1
                    non_canonicals[token].candidates.append(prediction)

        except AssertionError:
            print("Invalid data format")
            sys.exit(1)

    write_to_file(non_canonicals)

    # calc p, r, f
    p = correct_norm / total_norm
    r = correct_norm / total_nsw
    print("Evaluating {}".format(pred_file))
    if p != 0 and r != 0:
        f1 = (2 * p * r) / (p + r)
        print("precision: {}".format(round(p, 4)))
        print("recall:   {}".format(round(r, 4)))
        print("F1:       {}".format(round(f1, 4)))
    else:
        print("precision: {}".format(round(p, 4)))
        print("recall:   {}".format(round(r, 4)))


def write_to_file(output):
    output = dict(reversed(
        sorted(output.items(), key=lambda kv: kv[1].count)))

    with open("error_out.txt", "w+") as error_file:
        error_file.write("{}\t{}\t{}\t{}".format("Token",
                                                 "Canoncical", "Freq", "Actual") + "\n")
        for token in output:
            error_file.write("{}\t{}\t{}\t{}".format(token,
                                                     output[token].canonical, output[token].count, output[token].candidates) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluation scripts for LexNorm in W-NUT 2015")
    parser.add_argument("--pred", required=True,
                        help="A JSON file: Your predictions over test data formatted in JSON as training data")
    parser.add_argument("--oracle", required=True,
                        help="A JSON file: The oracle annotations of test data formatted in JSON as training data")
    args = parser.parse_args()

    evaluate(args.pred, args.oracle)


if __name__ == "__main__":
    main()
