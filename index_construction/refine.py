from utils import file_line_to_term_index, term_index_to_file_line, save_map
from printer import RefinePrinter


class Refiner(object):

    def __init__(self, collection, weighter, verbose):
        # type: (Collection, Weighter, bool) -> None
        self._collection = collection
        self.n_d = dict()
        self.positions = dict()
        self.weighter = weighter
        self.printer = RefinePrinter(verbose)

    def refine_index(self):
        stuff_to_write = list()
        self.printer.print_refine_start_message()
        with open("indexes/%s.index" % self._collection.collection_path) as index_file:
            for counter, line in enumerate(index_file):
                term_index = file_line_to_term_index(line)
                stuff_to_write.append((term_index[0], self.refine_line(term_index)))
        # TODO: don't forget about Nds (that are set to 1 for the moment)
                if counter % 25000 == 0:
                    self.printer.print_refine_progress_message(counter)
        with open("indexes/%s.refined.index" % self._collection.collection_path, 'w') as refined_file:
            for stuff in stuff_to_write:
                self.positions[int(stuff[0])] = refined_file.tell()
                refined_file.write(term_index_to_file_line(stuff))
        save_map(self.positions, "indexes/" + self._collection.collection_path + "/positions")
        self.printer.print_end_of_refine_message()

    def refine_line(self, index_line):
        term_id, posting_list = index_line
        if self.weighter.weight_function_id == 6:
            cf = sum([f for d_id, f in posting_list])
            new_posting_list = [(doc, freq, self.weighter.weight(doc, freq, len(posting_list), cf))
                                for doc, freq in posting_list]
        else:
            new_posting_list = [(doc, freq, self.weighter.weight(doc, freq, len(posting_list)))
                                for doc, freq in posting_list]
        # self.n_d[doc_id] = self.n_d.get(doc_id, 0) + temp_weight*temp_weight
        # / ! \ Nd not computed any more!
        return new_posting_list
