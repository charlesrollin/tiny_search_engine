from math import log10, sqrt

# All the weights described here are taken from http://ir.dcs.gla.ac.uk/~ronanc/papers/cumminsChapter.pdf
from threading import Lock


class WeightFactory(object):
    """List all the existing implementations of Weighter and serve them."""

    weightClasses = list()

    @staticmethod
    def get_weight_function(weight_function_id, collection_size):
        return WeightFactory.weightClasses[weight_function_id](weight_function_id, collection_size)


class Weighter(object):
    """Compute a weight and store a CollectionStats object.

    Any implementation of a weight function must inherit from this class and be decorated with the declare_subclass
    method in order to be declared to the WeightFactory (see examples below).
    """

    @classmethod
    def declare_weighter(cls):
        WeightFactory.weightClasses.append(cls)

    def __init__(self, weight_id, collection_size):
        self.stats = CollectionStats(collection_size)
        self.weight_function_id = weight_id

    def weight(self, doc_id, *args):
        """Compute the weight of a term in a document.

        *args is the data from the index needed to compute the weight (usually td and df).
        Extra data will be fetched directly by this class from its stats object.
        """
        return self._weight_function(*(list(args) + self._get_stat_args(doc_id)))

    def _weight_function(self, *args):
        # This method is meant to be abstract. Any extension of the Weighter class must implement it!
        raise NotImplementedError

    def _get_stat_args(self, doc_id):
        """Retrieve from self.stats the data needed to compute a weight."""
        raise NotImplementedError


def declare_subclass(cls):
    """Decorator to automatically declare a sub-class of Weighter to WeighterFactory."""
    cls.declare_weighter()


@declare_subclass
class TfIdf(Weighter):

    def _weight_function(self, tf, df, collection_size):
        return tf * log10(collection_size / float(df))

    def _get_stat_args(self, doc_id):
        return [self.stats.get_collection_size()]


@declare_subclass
class NormalizedTfIdf(Weighter):

    def _weight_function(self, tf, df, collection_size):
        return (1 + log10(tf)) * log10(collection_size / float(df))

    def _get_stat_args(self, doc_id):
        return [self.stats.get_collection_size()]


@declare_subclass
class NormalizedFrequency(Weighter):

    def _weight_function(self, tf, df, max_freq):
        return tf / float(max_freq)

    def _get_stat_args(self, doc_id):
        return [self.stats.get_doc_max_freq(doc_id)]


@declare_subclass
class PivotedDocumentLengthNormalization(Weighter):

    def _weight_function(self, tf, df, collection_size, doc_length, average_length):
        """Pivoted Document Length Normalization. """
        s = 0.2
        tf_piv = (1 + log10(1 + log10(tf))) / (1 - s + s * doc_length / float(average_length))
        idf_piv = log10((collection_size + 1) / float(df))
        return tf_piv * idf_piv

    def _get_stat_args(self, d_id):
        return [self.stats.get_collection_size(), self.stats.get_doc_length(d_id), self.stats.get_average_doc_length()]


@declare_subclass
class BM25(Weighter):

    def _weight_function(self, tf, df, collection_size, doc_length, average_length):
        k, b = 2, 0.75
        tf_bm25 = tf * (k + 1) / (tf + k * (1 - b + b * doc_length / float(average_length)))
        idf_bm25 = log10((collection_size - df + 0.5) / (df + 0.5))
        return tf_bm25 * idf_bm25

    def _get_stat_args(self, d_id):
        return [self.stats.get_collection_size(), self.stats.get_doc_length(d_id), self.stats.get_average_doc_length()]


@declare_subclass
class ModifiedBM25(Weighter):

    def _weight_function(self, tf, df, collection_size, doc_length, average_length):
        """Modified BM25."""
        k, b = 2, 0.75
        tf_mbm25 = tf * (k + 1) / (tf + k * (1 - b + b * doc_length / float(average_length)))
        idf_mbm25 = log10((collection_size + 1) / float(df))
        return tf_mbm25 * idf_mbm25

    def _get_stat_args(self, d_id):
        return [self.stats.get_collection_size(), self.stats.get_doc_length(d_id), self.stats.get_average_doc_length()]


@declare_subclass
class EvolutionaryLearnedScheme(Weighter):

    def _weight_function(self, tf, df, cf, collection_size, doc_length, average_length):
        """Evolutionary Learned Scheme."""
        tf_es = tf / (tf + 0.45 + sqrt(doc_length / float(average_length)))
        idf_es = sqrt(cf*cf*cf*collection_size / float(df*df*df*df))
        return tf_es*idf_es

    def _get_stat_args(self, d_id):
        return [self.stats.get_collection_size(), self.stats.get_doc_length(d_id), self.stats.get_average_doc_length()]


@declare_subclass
class DivergenceFromRandomness(Weighter):

    def _weight_function(self, tf, df, collection_size, doc_length, average_length):
        """Divergence From Randomness."""
        tf_dfr = tf * log10(1 + average_length / float(doc_length)) \
                 / (1 + tf*log10(1 + average_length / float(doc_length)))
        idf_dfr = log10((collection_size + 1) / (df + 0.5))
        return tf_dfr * idf_dfr

    def _get_stat_args(self, d_id):
        return [self.stats.get_collection_size(), self.stats.get_doc_length(d_id), self.stats.get_average_doc_length()]


@declare_subclass
class AxiomaticScheme(Weighter):

    def _weight_function(self, tf, df, collection_size, doc_length, average_length):
        """Axiomatic Term-Weighting Scheme."""
        tf_2exp = tf / (tf + 0.5 + 0.5*doc_length / float(average_length))
        idf_2exp = pow(collection_size, 0.35) / float(df)
        return tf_2exp*idf_2exp

    def _get_stat_args(self, d_id):
        return [self.stats.get_collection_size(), self.stats.get_doc_length(d_id), self.stats.get_average_doc_length()]


class CollectionStats(object):
    """Store statistics on the processed collection."""

    def __init__(self, collection_size):
        self.docs_stats = dict()
        self.average_doc_length = 0
        self.collection_size = collection_size
        self.lock = Lock()

    def process_posting_list(self, posting_list):
        """Update the statistics with a new posting list."""
        with self.lock:
            for doc_id, freq in posting_list:
                length, max_freq = self.docs_stats.get(doc_id, (0, 0))
                length += freq
                self.average_doc_length += freq
                if freq > max_freq:
                    max_freq = freq
                self.docs_stats[doc_id] = length, max_freq

    def signal_end_of_merge(self):
        self.average_doc_length /= float(self.collection_size)

    def get_collection_size(self):
        return self.collection_size

    def get_average_doc_length(self):
        return self.average_doc_length

    def get_doc_length(self, doc_id):
        return self.docs_stats[doc_id][0]

    def get_doc_max_freq(self, doc_id):
        return self.docs_stats[doc_id][1]
