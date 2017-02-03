import time

from index_construction.merge import BlockIndexMerger
from index_construction.parse import DefaultParseManager
from index_construction.refine import Refiner
from index_construction.weights import WeightFactory


def build_index(collection, weight_function_id, verbose):
    # type: (Collection) -> dict
    p = DefaultParseManager(verbose)
    start = time.time()
    p.parse(collection)
    parsing_end = time.time()
    del p
    collection.store_maps()
    weighter = WeightFactory.get_weight_function(weight_function_id, len(collection))
    b = BlockIndexMerger(collection, weighter.stats, 220, verbose)
    b.merge()
    merging_end = time.time()
    r = Refiner(collection, weighter, verbose)
    positions = r.refine_index()
    refining_end = time.time()
    tot = refining_end - start
    print("Index built in %.2f sec:\n\tParse: %.2f sec\n\tMerge: %.2f sec\n\tRefine: %.2f sec"
          % (tot, parsing_end - start, merging_end - parsing_end, refining_end - merging_end))
    return positions
