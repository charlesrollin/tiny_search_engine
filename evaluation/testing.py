from collection import Collection
from evaluation.measures import EvaluationBuilder
from index_construction.main import build_index
from index_construction.weights import WeightFactory
from printer import TestPrinter
from queries.vector_queries import VectorQueryParser


class EvaluatedQuery(object):

    def __init__(self, raw_query, relevant_docs):
        self.query = raw_query
        self.relevant_docs = relevant_docs

    def match_result(self, document):
        if document[17:-5] in self.relevant_docs:
                return True
        return False

    def __str__(self):
        s = "Query: %s" % self.query
        s += "\n\twith relevant docs: %s" % self.relevant_docs
        return s


class TestBuilder(object):

    def __init__(self, queries_file_path, results_file_path):
        queries_list = self._build_queries_list(queries_file_path)
        results_list = self._build_results_list(results_file_path)
        self.queries = [EvaluatedQuery(queries_list[i], results_list[i]) for i in range(len(queries_list))]
        self.printer = TestPrinter()

    def _build_queries_list(self, queries_file_path):
        storing = False
        result = list()
        temp = ""
        with open(queries_file_path) as queries_file:
            for line in queries_file:
                if line[:2] == ".W":
                    storing = True
                    if temp != "":
                        result.append(temp)
                        temp = ""
                elif line[:1] == ".":
                    storing = False
                elif storing:
                    temp += line
        result.append(temp)
        return result

    def _build_results_list(self, results_file_path):
        counter = 1
        results = list()
        with open(results_file_path) as results_file:
            query_results = list()
            for result in results_file:
                splitted = result.split()
                if int(splitted[0]) == counter:
                    query_results.append(str(int(splitted[1])))
                else:
                    results.append(query_results)
                    query_results = [str(int(splitted[1]))]
                    counter += 1
        results.append(query_results)
        return results

    def test(self, collection_path):
        # type: (str) -> None
        import matplotlib.pyplot as plt
        for i in range(len(WeightFactory.weightClasses)):
            self.printer.print_test_progress(i+1, len(WeightFactory.weightClasses))
            curve = self._weight_test(collection_path, i)
            plt.plot(*zip(*curve.points), marker="x", label="#%i (MAP: %.3f)" % (i+1, curve.get_mean_average_precision()))
        plt.legend(loc='upper right', shadow=True, fontsize='x-large')
        plt.xlabel("Recall")
        plt.xlim((0, 1))
        plt.ylabel("Precision")
        plt.ylim((0, 1))
        plt.show()

    def _weight_test(self, collection_path, weight_function_id):
        # type: (str, int) -> MeanCurve
        c = Collection(collection_path, verbose=False)
        positions = build_index(c, weight_function_id, verbose=False)
        runner = VectorQueryParser(c, "indexes/%s.index" % c.collection_path, positions, verbose=False)
        eb = EvaluationBuilder()
        query_counter = 0
        for sup_query in self.queries:
            query_counter += 1
            results = runner.execute_query(sup_query.query)
            eb.evaluate_query(sup_query, results)
        eb.normalize()
        return eb.results.prCurve

    def __str__(self):
        s = ""
        for query in self.queries:
            s += str(query) + "\n"
        return s
