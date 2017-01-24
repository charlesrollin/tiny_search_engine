import argparse
from math import log
from old_parse import Parser
from old_parse import Cleaner
from old_parse import HeapsRuler
from matplotlib import pyplot as plt


def start_parsing(parser, cleaner, parsing_ratio=100):
    tokens_amount, tokens = parser.parse(parsing_ratio)
    terms = cleaner.clean(tokens)
    print("\tAmount of tokens: %s" % tokens_amount)
    print("\tAmount of terms: %s" % len(terms))
    return terms, tokens_amount


def main(mode):
    p = Parser(mode)
    super_size = 1000000
    c = Cleaner(mode, "./common_words")
    terms1, tokens_size1 = start_parsing(p, c)
    terms2, tokens_size2 = start_parsing(p, c, 50)
    hri = HeapsRuler((len(terms1), len(terms2)), (tokens_size1, tokens_size2))
    print("Size of vocabulary with a collection of %s tokens: %s" % (super_size, hri.estimate_voc_size(super_size)))
    f, axarr = plt.subplots(2)
    lin_plot_list = [(i+1, terms1[i][1]) for i in range(len(terms1))]
    log_plot_list = [(log(i+1), log(terms1[i][1])) for i in range(len(terms1))]
    axarr[0].set_title('frequence vs rang')
    axarr[0].plot(*zip(*lin_plot_list))
    axarr[1].set_title('log(frequence) vs log(rang)')
    axarr[1].plot(*zip(*log_plot_list))
    plt.show()

argparser = argparse.ArgumentParser()
argparser.add_argument("collection", help="the collection to analyse, 'cs' or 'cacm'")
args = argparser.parse_args()
if args.collection not in ['cs', 'cacm']:
    exit(2)
else:
    main(args.collection)
