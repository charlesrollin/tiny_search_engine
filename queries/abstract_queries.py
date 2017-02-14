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
