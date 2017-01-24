# TODO: automate calls to complete_curve and normalize methods?


class Curve(object):

    def __init__(self):
        self.points = list()
        self._raw_points = list()

    def add(self, point):
        self._raw_points.append(point)
        if len(self.points) == 0 or self.points[-1][1] >= point[1]:
            self.points.append(point)
        else:
            self.points = self.points[:-1]
            self.add(point)

    def complete_curve(self):
        """Signal that no other point will be added to this curve."""
        if not (len(self.points) > 0 and self.points[-1][0] == 1):
            self.points.append((1, 0))

    def evaluate(self, recall):
        """
        Evaluate curve via binary search (might be an overkill).
        """
        begin = 0
        end = len(self.points)
        index = begin + (end - begin) // 2
        while end - begin > 1:
            current_recall = self.points[index][0]
            if current_recall < recall:
                begin = index
            elif current_recall == recall:
                return self.points[index][1]
            else:
                end = index
            index = begin + (end - begin) // 2
        return self.points[begin][1] if self.points[begin][0] >= recall else self.points[end][1]

    def __len__(self):
        return len(self.points)

    def __getitem__(self, item):
        return self.points[item]


class InterpolatedCurve(object):
    """The 11-points interpolation of a curve defined on [0, 1]."""

    def __init__(self, curve):
        # type: (Curve) -> None
        self.points = list()
        extrapolated_points = [0.1 * i for i in range(11)]
        for i, recall in enumerate(extrapolated_points):
            self.points.append((recall, curve.evaluate(recall)))
            if i < len(extrapolated_points) - 1:
                self.points.append((recall, curve.evaluate(extrapolated_points[i + 1])))


class MeanCurve(object):
    """The mean of a set of curves.

    To simplify calculations, the curves must be instances of InterpolatedCurve.
    """

    def __init__(self):
        self.points = list()
        self._weight = 0

    def add(self, curve):
        # type: (InterpolatedCurve) -> None
        if len(self.points) == 0:
            self.points = curve.points
        else:
            for i, (recall, precision) in enumerate(self.points):
                self.points[i] = (recall, precision + curve.points[i][1])
        self._weight += 1

    def normalize(self):
        self.points = [(recall, precision / self._weight) for recall, precision in self.points]

    def get_mean_average_precision(self):
        return sum([precision for recall, precision in self.points]) / 11.0
