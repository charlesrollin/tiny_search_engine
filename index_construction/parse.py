from threading import Thread
from utils import make_dirs

from printer import ParsePrinter


class AbstractParseManager(object):

    def __init__(self, verbose):
        self._cleaner = Cleaner()
        self.printer = ParsePrinter(verbose)

    def parse(self, collection):
        """Start BlockParser workers on each block of the collection."""
        raise NotImplementedError


class DefaultParseManager(AbstractParseManager):

    def parse(self, collection):
        block_parsers = [DefaultBlockParser(block, collection.id_storer, self._cleaner, self.printer)
                         for block in collection.blocks]
        for parser in block_parsers:
            parser.start()
        for parser in block_parsers:
            parser.join()


class AbstractBlockParser(Thread):

    def __init__(self, block, id_storer, cleaner, printer):
        Thread.__init__(self)
        self._cleaner = cleaner
        self.printer = printer
        self.block = block
        self.id_storer = id_storer

    def _process_line(self, line):
        raise NotImplementedError

    def run(self):
        block = self.block
        id_storer = self.id_storer
        self.printer.print_block_parse_start_message(block.block_path)
        tokens_amount = 0
        reversed_index = dict()
        for doc_id in block.documents:
            doc_frequency_dict = dict()
            with open(id_storer.doc_map[doc_id]) as my_file:
                for line in my_file:
                    for word in self._process_line(line):
                        tokens_amount += 1
                        doc_frequency_dict[word] = doc_frequency_dict.get(word, 0) + 1
            doc_frequency_dict = {w: v for w, v in doc_frequency_dict.items() if not self._cleaner.is_common_word(w)}
            for word in doc_frequency_dict.keys():
                term_id = id_storer.term_map[word] if word in id_storer.term_map else id_storer.add_term(word)
                occurrence_list = reversed_index.get(term_id, list())
                occurrence_list.append((doc_id, doc_frequency_dict[word]))
                reversed_index[term_id] = occurrence_list
        self._write_block_index("indexes/" + block.block_path, reversed_index)
        self.printer.print_block_parse_end_message(block.block_path)

    def _write_block_index(self, file_path, block_index):
        lines_to_write = list()
        for term_id in sorted(block_index):
            result = "%s:" % term_id
            for occurrence in block_index[term_id]:
                result += "%s,%s|" % occurrence
            lines_to_write.append(result[:-1] + "\n")
        make_dirs(file_path)
        with open(file_path, "w") as block_index_file:
            block_index_file.writelines(lines_to_write)


class DefaultBlockParser(AbstractBlockParser):

    def _process_line(self, line):
        return line.split()


class Cleaner(object):

    def __init__(self, common_words_file="common_words"):
        self._common_words = dict()
        with open(common_words_file) as my_file:
            for line in my_file:
                self._common_words[line[:-1]] = True

    def is_common_word(self, word):
        return word in self._common_words
