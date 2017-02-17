import operator

import re

from queries.abstract_queries import AbstractQueryParser
from porterstemmer import Stemmer


class VectorQueryParser(AbstractQueryParser):

    def _clean_query(self, query):
        stemmer = Stemmer()
        result = ""
        for word in filter(None, re.split('[^a-zA-Z\d:]', query)):
            result += stemmer(word.lower()) + " "
        return result

    def execute_query(self, query):
        score = dict()
        freqs = dict()
        query = self._clean_query(query)
        term_map = self.collection.id_storer.term_map
        term_ids = [term_map[w] for w in query.split() if w in term_map]
        for id in term_ids:
            freqs[id] = freqs.get(id, 0) + 1
        # To avoid unnecessary reads to index, we will work with freqs (contains no duplicates)
        posting_lists = self._index_reader.read(freqs.keys(), refined=True)
        for term_id in posting_lists:
            for doc_id, weight in posting_lists[term_id]:
                score[doc_id] = score.get(doc_id, 0) + weight * freqs[term_id]
        results = sorted(score.items(), key=operator.itemgetter(1), reverse=True)
        self.printer.print_results([(self.collection.id_storer.doc_map[d_id], score) for d_id, score in results[:10]],
                                   len(results))
        return [self.collection.id_storer.doc_map[result[0]] for result in results]
