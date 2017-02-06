import time

from index_construction.merge import BlockIndexMerger
from index_construction.parse import DefaultParseManager
from index_construction.weights import WeightFactory


def build_index(collection, weight_function_id, verbose, memory=1100):
    weighter = WeightFactory.get_weight_function(weight_function_id, len(collection))
    p = DefaultParseManager(weighter.stats, verbose)
    start = time.time()
    p.parse(collection)
    parsing_end = time.time()
    del p
    collection.store_maps()
    b = BlockIndexMerger(collection, weighter, memory, verbose)
    positions = b.merge()
    merging_end = time.time()
    tot = merging_end - start
    print("Index built in %.2f sec:\n\tParse: %.2f sec\n\tMerge: %.2f sec"
          % (tot, parsing_end - start, merging_end - parsing_end))
    return positions
