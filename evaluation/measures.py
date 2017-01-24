from evaluation.curves import MeanCurve, Curve, InterpolatedCurve


def e_measure(precision, recall, beta=1):
    return 1 - (beta*beta + 1) * precision * recall / (beta*beta*precision + recall)


def f_measure(precision, recall, beta=1):
    return 1 - e_measure(precision, recall, beta)


class EvaluationResults(object):

    def __init__(self):
        self.prCurve = MeanCurve()
        self.eCurve = MeanCurve()
        self.fCurve = MeanCurve()


class EvaluationBuilder(object):

    def __init__(self):
        self.results = EvaluationResults()

    def evaluate_query(self, sup_query, results):
        # type: (SupervisedQuery, list) -> None
        pr = Curve()
        e = Curve()
        f = Curve()
        relevant_docs = 0
        for i, result in enumerate(results):
            if sup_query.match_result(result):
                relevant_docs += 1
                precision = relevant_docs / float(i + 1)
                recall = relevant_docs / float(len(sup_query.relevant_docs))
                pr.add((recall, precision))
                e.add((recall, e_measure(precision, recall)))
                f.add((recall, f_measure(precision, recall)))
        pr.complete_curve()
        e.complete_curve()
        f.complete_curve()
        self.results.prCurve.add(InterpolatedCurve(pr))
        self.results.eCurve.add(InterpolatedCurve(e))
        self.results.fCurve.add(InterpolatedCurve(f))

    def normalize(self):
        self.results.prCurve.normalize()
        self.results.eCurve.normalize()
        self.results.fCurve.normalize()
