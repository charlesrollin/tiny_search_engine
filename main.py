import argparse
import textwrap
from argparse import RawTextHelpFormatter

from collection import Collection
from evaluation.main import run_test
from index_construction.main import build_index
from index_construction.weights import WeightFactory
from utils import load_map
from queries.boolean_queries import BooleanQueryParser
from queries.vector_queries import VectorQueryParser


def run(collection_name, force_new_index, weight_function_id, start_evaluation, memory):
    collection_path = collection_name + "-data"
    if start_evaluation:
        run_test(collection_path, "queries/query.text", "queries/qrels.text")
    else:
        c = Collection(collection_path, verbose=True)
        if force_new_index:
            positions = build_index(c, weight_function_id, verbose=True, memory=memory)
        else:
            c.id_storer.term_map = load_map("indexes/" + c.collection_path + "/termmap", value_type=int)
            positions = load_map("indexes/" + c.collection_path + "/positions", key_type=int, value_type=int)
        runner = VectorQueryParser(c, "indexes/%s.index" % c.collection_path, positions, verbose=True)
        while True:
                runner.execute_query(input("Enter your query: "))


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    arg_parser.add_argument("collection", help="the collection to analyse, 'cs276' or 'cacm'")
    help_str = "".join(["%i: %s\n" % (i, weighter.__name__) for i, weighter in enumerate(WeightFactory.weightClasses)])
    arg_parser.add_argument('-w', '--weight', default=0, type=int, help=textwrap.dedent(help_str))
    arg_parser.add_argument('-r', '--refresh', help="add this flag to force refresh of index", action="store_true")
    arg_parser.add_argument('-e', '--evaluate', help="add this flag to launch engine evaluation", action="store_true")
    arg_parser.add_argument('-m', '--memory', default=2200, type=int, help="set memory limitations")
    args = arg_parser.parse_args()
    if args.collection not in ['cs276', 'cacm']:
        print("\tThe %s collection is not supported yet..." % args.collection)
        exit(2)
    if args.weight < 0 or args.weight >= len(WeightFactory.weightClasses):
        print("\tThe specified weight function is not valid...")
        exit(2)
    if args.evaluate and args.collection == 'cs276':
        print("\tEngine evaluation is only supported for the cacm collection...")
        exit(2)
    run(args.collection, args.refresh, args.weight, args.evaluate, args.memory)
