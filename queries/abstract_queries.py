from utils import file_line_to_term_index
from printer import QueryParserPrinter


class _CollectionIndexReader(object):
    """
    A Read interface for an index file.
    """

    def __init__(self, index_path, positions):
        # type: (str, dict{int: int}) -> None
        """
        :type positions: dict of (int, int)
        :param index_path: the path to the index file
        :param positions: {term_id: position_in_index_file}
        """
        self._index_path = index_path
        self._positions = positions

    def read(self, term_ids, refined=False):
        # type: (list[int], bool) -> dict
        """
        Get the posting lists of a list of term ids.
        :type term_ids: list of int
        :param term_ids:
        :param refined:
        :return: a list of posting lists
        """
        result = dict()
        with open(self._index_path) as index_file:
            for term_id in term_ids:
                try:
                    index_file.seek(self._positions[term_id])
                    result[term_id] = file_line_to_term_index(index_file.readline(), refined=refined)[1]
                except KeyError:
                    result[term_id] = list()
        return result


class AbstractQueryParser(object):

    def __init__(self, collection, index_path, positions, verbose):
        # type: (Collection, str, dict{int: int}) -> None
        """
        :type positions: dict of (int, int)
        :param collection: the working collection
        :param index_path: the file of the index file
        :param positions: {term_id: position_in_index_file}
        """
        self.collection = collection
        self._index_reader = _CollectionIndexReader(index_path, positions)
        self.printer = QueryParserPrinter(verbose)

    def execute_query(self, query):
        # type: (str) -> None
        """
        Execute a query
        """
        # This method is meant to be abstract. Any extension of the QueryParser class must implement it!
        raise NotImplementedError
