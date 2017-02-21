import heapq
import operator
from threading import Thread
import time

from utils import bin_to_term_index
from printer import QueryParserPrinter


class _CollectionIndexReader(object):
    """
    A Read interface for an index file.
    """

    def __init__(self, index_path, positions):
        """
        :param index_path: the path to the index file
        :param positions: a deque of the positions in the index
        """
        self._index_path = index_path
        self._positions = positions

    def read(self, term_ids, refined=False):
        """
        Get the posting lists of a list of term ids.
        :type term_ids: list of int
        :param term_ids:
        :param refined:
        :return: a list of posting lists
        """
        result = dict()
        with open(self._index_path, 'rb') as index_file:
            for term_id in term_ids:
                try:
                    index = term_id - 1
                    index_file.seek(self._positions[index])
                    if index == len(self._positions) - 1:
                        size = -1
                    else:
                        size = self._positions[index + 1] - self._positions[index]
                    result[term_id] = bin_to_term_index(index_file.read(size), refined=refined)[1]
                except KeyError:
                    result[term_id] = list()
        return result


class Results(Thread):

    def __init__(self, results, id_storer, capacity=10):
        Thread.__init__(self, daemon=True)
        self._status = False  # True iff self._results is completely sorted
        self._raw_results = results
        self._id_storer = id_storer
        self._length = len(results)
        self._capacity = capacity
        self._results = list()
        self._cursor = 0

    def __len__(self):
        return self._length

    def run(self):
        self._results.append(self._top_k())
        self._raw_results.sort(key=operator.itemgetter(1))
        self._status = True

    def next(self):
        while self._cursor != 0 and not self._status:
            time.sleep(0.05)
        if len(self._results) - 1 < self._cursor:
            temp = list()
            for _ in range(min(self._capacity, len(self._raw_results))):
                doc_id, score = self._raw_results.pop()
                temp.append((self._id_storer.doc_map[doc_id], score))
            self._results.append(temp)
        self._cursor += 1
        return self._results[self._cursor - 1]

    def get_all(self):
        results = list()
        for result in self._results:
            results += result
        return results

    def _top_k(self):
        capacity = min(self._capacity, len(self))
        heap = self._raw_results[:capacity]
        for doc_id, score in self._raw_results[capacity:]:
            heapq.heappushpop(heap, (score, doc_id))
        result = list()
        for _ in range(capacity):
            score, doc_id = heapq.heappop(heap)
            result.append((self._id_storer.doc_map[doc_id], score))
        result.reverse()
        return result

    def _background_sort(self):
        self._raw_results = sorted(self._raw_results)  # no in-place sort to avoid inconsistent state of _results


class AbstractQueryParser(object):

    def __init__(self, collection, index_path, positions, verbose):
        """
        :param collection: the working collection
        :param index_path: the file of the index file
        :param positions: {term_id: position_in_index_file}
        """
        self.collection = collection
        self._index_reader = _CollectionIndexReader(index_path, positions)
        self.printer = QueryParserPrinter(verbose)

    def execute_query(self, query):
        """
        Execute a query
        """
        raise NotImplementedError
