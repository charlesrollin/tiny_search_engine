from os import remove

from index_construction.index_IO import SequentialIndexWriter, SequentialIndexReader
from printer import MergePrinter
from utils import save_positions


class BlockIndexMerger(object):

    def __init__(self, collection, block_positions, weighter, total_capacity, verbose):
        self._collection = collection
        self._readers = list()
        self._capacity = total_capacity / (len(collection.blocks) + 1)
        for block in collection.blocks:
            self._readers.append(SequentialIndexReader("indexes/" + block.block_path,
                                                       block_positions[block.block_path], self._capacity))
        self._writer = SequentialIndexWriter("indexes/" + self._collection.collection_path + ".index", self._capacity,
                                             refined=True)
        self.weighter = weighter
        self.printer = MergePrinter(verbose)

    def _get_lexically_first(self):
        result = float("inf")
        reader_id = -1
        for i in range(len(self._readers)):
            reader = self._readers[i]
            item = reader.peek()
            if item is not None and int(item[0]) < result:
                result = int(item[0])
                reader_id = i
        return None if reader_id < 0 else self._readers[reader_id].pop()

    def _end(self):
        for reader in self._readers:
            remove(reader.file_path)
        self._writer.close()

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

    def merge(self):
        self.printer.print_merge_start_message()
        counter = 0
        last_term = self._get_lexically_first()
        while last_term is not None:
            next_term = self._get_lexically_first()
            if next_term is not None and last_term[0] == next_term[0]:
                last_term = last_term[0], (last_term[1] + next_term[1])
            else:
                self._writer.append((last_term[0], self.refine_line(last_term)))
                counter += 1
                last_term = next_term
                if counter % 25000 == 0:
                    self.printer.print_merge_progress_message(counter)
        self.printer.print_end_of_merge_message(counter)
        self._end()
        save_positions(self._writer.positions, "indexes/" + self._collection.collection_path + "/positions")
        return self._writer.positions
