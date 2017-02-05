from index_construction.index_IO import SequentialIndexReader, SequentialIndexWriter
from utils import save_map
from printer import RefinePrinter


# TODO: share IndexWriter class to avoid loading the entire index in memory!
class Refiner(object):

    def __init__(self, collection, weighter, verbose, capacity):
        self._collection = collection
        self.n_d = dict()
        self.capacity = capacity
        self.positions = dict()
        self.weighter = weighter
        self.printer = RefinePrinter(verbose)

    def refine_index(self):
        reader = SequentialIndexReader("indexes/%s.index" % self._collection.collection_path, self.capacity / 2)
        writer = SequentialIndexWriter("indexes/%s.refined.index" % self._collection.collection_path,
                                       self.capacity / 2, refined=True)
        self.printer.print_refine_start_message()
        counter = 0
        while reader.peek() is not None:
            term_index = reader.pop()
            writer.append((term_index[0], self.refine_line(term_index)))
            if counter % 25000 == 0:
                self.printer.print_refine_progress_message(counter)
            counter += 1
        # TODO: don't forget about Nds (that are set to 1 for the moment)
        save_map(writer.positions, "indexes/" + self._collection.collection_path + "/positions")
        self.printer.print_end_of_refine_message()
        return writer.positions

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
