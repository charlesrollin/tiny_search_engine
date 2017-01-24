import re
import operator
from os import listdir
from math import log


class Document(object):

    def __init__(self, title):
        self.title = title  # or maybe documents should be stored in {title: document} dictionaries?
        self.words = dict()


class Parser(object):

    def __init__(self, mode):
        self._interesting_markers = ['.I', '.T', '.W', 'K']
        self._markers = ['.I', '.T', '.W', '.B', '.A', '.N', '.X', '.K']
        self.parse = self._cs_parse if mode == 'cs' else self._cacm_parse
        self._file_name = "./cs276-data" if mode == 'cs' else "./cacm-data/0/cacm.all"

    def _is_marker(self, line_begin):
        return line_begin in self._markers

    def _is_interesting_marker(self, line_begin):
        return line_begin in self._interesting_markers

    def _cacm_parse(self, parsing_ratio=100):
        """
        Split each line of a portion of the documents of a collection into a list of words.
        :param parsing_ratio: the ratio (in percent) of the documents of the collection to parse
        :return: the amount of tokens and the list of them in the considered documents
        """
        print("Parsing %s percent of the collection..." % parsing_ratio)
        doc_counter = 0
        storing = False
        result = list()
        with open(self._file_name, 'r') as my_file:
            for line in my_file:
                line_begin = line[0:2]
                if not self._is_marker(line_begin):
                    if storing:
                        for word in filter(None, re.split('[^a-zA-Z\d:]', line)):
                            if parsing_ratio != 100:
                                result.append((word.lower(), doc_counter))
                            else:
                                result.append(word.lower())
                else:
                    if self._is_interesting_marker(line_begin):
                        if line_begin == '.I':
                            doc_counter += 1
                        storing = True
                    else:
                        storing = False
        if parsing_ratio != 100:
            result = [word[0] for word in result if 100*word[1] / doc_counter <= parsing_ratio]
        return len(result), result

    def _cs_parse(self, parsing_ratio=100):
        """
        Split each line of a portion of the documents of a collection into a dict of {word: frequency}.
        :param parsing_ratio: the ratio (in percent) of the documents of the collection to parse
        :return: the amount of tokens and the dict of their frequencies
        """
        print("Parsing %s percent of the collection..." % parsing_ratio)
        tokens_amount = 0
        words = dict()
        for i in range(10 * parsing_ratio / 100):
            for file in listdir(self._file_name + "/" + str(i)):
                with open(self._file_name + "/" + str(i) + "/" + file) as my_file:
                    for line in my_file:
                        for word in line.split():
                            tokens_amount += 1
                            # words[word] = words.get(word, 0) + 1
                            words[word] = words[word] + 1 if word in words else 1
        return tokens_amount, words


class Cleaner(object):

    def __init__(self, mode, common_words_file):
        self._common_words = dict()
        with open(common_words_file) as my_file:
            for line in my_file:
                self._common_words[line[:-1]] = True
        self.clean = self._cs_clean if mode == 'cs' else self._cacm_clean

    def _cacm_clean(self, words):
        """
        Remove common words and duplicates from a list of words, then sort the list by the frequency of each word.
        """
        result = dict()
        for word in words:
            if word not in self._common_words:
                result[word] = result.get(word, 0) + 1
        return sorted(result.items(), key=operator.itemgetter(1), reverse=True)

    def _cs_clean(self, dictionary):
        """
        Remove common words from a dict of {word: frequency}, then sort the dict by the frequency of each word.
        """
        result = dict()
        for word in dictionary.keys():
            if word not in self._common_words:
                result[word] = dictionary[word]
        return sorted(result.items(), key=operator.itemgetter(1), reverse=True)


class HeapsRuler(object):

    def __init__(self, vocabularies_sizes, tokens_sizes):
        self._identify_rule(vocabularies_sizes, tokens_sizes)

    def _identify_rule(self, vocabularies_sizes, tokens_sizes):
        m1, m2 = vocabularies_sizes
        t1, t2 = tokens_sizes
        self._b = log(m2 / float(m1)) / log(t2 / float(t1))
        self._k = m1 / pow(t1, self._b)
        print("Heaps law: M = k * T^b where:\n\t- k = %s\n\t- b = %s" % (self._k, self._b))

    def estimate_voc_size(self, tokens_size):
        """
        Process M = k * T ^b for a given T.
        """
        return self._k * pow(tokens_size, self._b)
