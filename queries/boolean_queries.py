import operator

import time

from queries.abstract_queries import AbstractQueryParser


class BooleanQueryParser(AbstractQueryParser):
    """
    Implementation of a query parser that handles boolean queries.

    Boolean queries must respect the following structure:
        - the query is written in CNF, i.e. a conjunction of disjunctions
        - disjunctions are separated with the && (AND) operator
        - a disjunction is a list of terms separated with the || (OR) operator and surrounded with parenthesis
    Two extra rules ensure that queries are well-defined:
        - the NOT operator can only apply to a disjunction (and not to a term)
            --> (foobar) && !(foo || bar) is well-defined
            --> (foobar) && (!foo || bar) is not (cf. end of doc)
        - the query must contain at least one not-negated disjunction
            --> (foobar) && !(foo || bar) is well-defined
            --> !(foo || bar) is not (cf. end of doc)

    About the NOT operator:
    This implementation assumes that the main use-case of the NOT operator is to filter an existing query,
    but not to get the complement of a query.
    Hence the two rules described above.
    """

    def execute_query(self, query):
        # type: (str) -> list
        """
        Execute a boolean query.
        :param query: a CNF query
        """
        start = time.time()
        docs = self._evaluate_query(query)
        results = sorted(docs, key=operator.itemgetter(1), reverse=True)
        self.printer.print_results([(self.collection.id_storer.doc_map[doc[0]], doc[1]) for doc in results],
                                   time.time() - start)
        return [self.collection.id_storer.doc_map[doc[0]] for doc in docs]

    def _get_word_from_disjunction(self, query):
        # type (str) -> list[str]
        return [word.lower() for word in query.split(" || ")]

    def _split_cnf_to_disjunctions(self, conjunction):
        """
        Split a raw CNF string into two lists of disjunctions.

        One list is for "positive" disjunctions and the other for "negative" disjunctions.
        """
        disjunctions = conjunction.split(" && ")
        words_from_disjunction = self._get_word_from_disjunction
        pos_disjs = [words_from_disjunction(disjunction[1:-1]) for disjunction in disjunctions if disjunction[0] != '!']
        neg_disjs = [words_from_disjunction(disjunction[2:-1]) for disjunction in disjunctions if disjunction[0] == '!']
        return pos_disjs, neg_disjs

    def _terms_cnf_to_ids_cnf(self, cnf):
        """
        Replace terms in a CNF by their id.

        Unknown terms are removed.
        """
        term_map = self.collection.id_storer.term_map
        return [[term_map[term] for term in disjunction if term in term_map] for disjunction in cnf]

    def _evaluate_query(self, query):
        pos_disjunctions, neg_disjunctions = self._split_cnf_to_disjunctions(query)
        pos_ids_cnf = self._terms_cnf_to_ids_cnf(pos_disjunctions)
        neg_ids_cnf = self._terms_cnf_to_ids_cnf(neg_disjunctions)
        pos_ids_cnf = [self._index_reader.read(term_ids, refined=True).values() for term_ids in pos_ids_cnf]
        neg_ids_cnf = [self._index_reader.read(term_ids, refined=True).values() for term_ids in neg_ids_cnf]
        conjunction = Conjunction((pos_ids_cnf, neg_ids_cnf))
        return conjunction.evaluate()


class Disjunction(object):
    """
    Representation of a disjunction of posting lists.
    """

    def __init__(self, posting_lists):
        self.posting_lists = posting_lists

    def __len__(self):
        return sum([len(posting_list) for posting_list in self.posting_lists])

    def evaluate(self):
        result = list()
        for posting_list in self.posting_lists:
            result = self._union(result, posting_list)
        return result

    def _union(self, occurrences1, occurrences2):
        """
        Return the set union between two posting lists.
        """
        index1, index2 = 0, 0
        result = list()
        while index1 + index2 < len(occurrences1) + len(occurrences2):
            if index2 >= len(occurrences2):
                result.append(occurrences1[index1])
                index1 += 1
            elif index1 >= len(occurrences1):
                result.append(occurrences2[index2])
                index2 += 1
            else:
                item1 = occurrences1[index1]
                item2 = occurrences2[index2]
                if item1[0] < item2[0]:
                    result.append(item1)
                    index1 += 1
                elif item1[0] > item2[0]:
                    result.append(item2)
                    index2 += 1
                else:
                    result.append(item1)
                    index1 += 1
                    index2 += 1
        return result


class Conjunction(object):
    """
    Representation of a CNF of posting lists.
    """

    def __init__(self, disjunctions):
        self._pos_disjunctions = sorted([Disjunction(disjunction) for disjunction in disjunctions[0]], key=len)
        self._neg_disjunctions = sorted([Disjunction(disjunction) for disjunction in disjunctions[1]], key=len)

    def evaluate(self):
        """
        Evaluate this CNF.
        :return: the postings that satisfy this CNF
        """
        if len(self._pos_disjunctions) == 0:
            print("\tQueries only containing negative disjunctions won't be processed!")
            return list()
        pos_result = self._evaluate_same_type_conjunction(self._pos_disjunctions)
        neg_result = self._evaluate_same_type_conjunction(self._neg_disjunctions)
        return self._diff(pos_result, neg_result)

    def _evaluate_same_type_conjunction(self, disjunctions):
        """
        Recursivel(ish)y evaluate a conjunction of disjunctions.
        """
        if len(disjunctions) == 0:
            return list()
        result = disjunctions[0].evaluate()
        for disjunction in disjunctions[1:]:
            result = self._intersection(result, disjunction.evaluate())
        return result

    def _intersection(self, occurrences1, occurrences2):
        """
        Return the set intersection between two posting lists.
        """
        index1, index2 = 0, 0
        result = list()
        while index1 + index2 < len(occurrences1) + len(occurrences2):
            if index2 >= len(occurrences2) or index1 >= len(occurrences1):
                break
            else:
                item1 = occurrences1[index1]
                item2 = occurrences2[index2]
                if item1[0] < item2[0]:
                    index1 += 1
                elif item1[0] > item2[0]:
                    index2 += 1
                else:
                    result.append(item1)
                    index1 += 1
                    index2 += 1
        return result

    def _diff(self, pos_occs, neg_occs):
        """
        Return the set difference between two posting lists.
        """
        index1, index2 = 0, 0
        result = list()
        while index1 + index2 < len(pos_occs) + len(neg_occs):
            if index1 >= len(pos_occs):
                break
            elif index2 >= len(neg_occs):
                result.append(pos_occs[index1])
                index1 += 1
            else:
                item1 = pos_occs[index1]
                item2 = neg_occs[index2]
                if item1[0] < item2[0]:
                    result.append(item1)
                    index1 += 1
                elif item1[0] > item2[0]:
                    index2 += 1
                else:
                    index1 += 1
                    index2 += 1
        return result
