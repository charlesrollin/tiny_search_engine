from os import remove

from index_construction.index_IO import SequentialIndexWriter, SequentialIndexReader
from printer import MergePrinter


class BlockIndexMerger(object):

    def __init__(self, collection, stats, total_capacity, verbose):
        self._collection = collection
        self._readers = list()
        self._capacity = total_capacity / (len(collection.blocks) + 1)
        for block in collection.blocks:
            self._readers.append(SequentialIndexReader("indexes/" + block.block_path, self._capacity))
        self._writer = SequentialIndexWriter("indexes/" + self._collection.collection_path + ".index", self._capacity)
        self.stats = stats
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

    def merge(self):
        self.printer.print_merge_start_message()
        counter = 0
        last_term = self._get_lexically_first()
        while last_term is not None:
            next_term = self._get_lexically_first()
            if next_term is not None and last_term[0] == next_term[0]:
                last_term = last_term[0], (last_term[1] + next_term[1])
            else:
                self.stats.process_posting_list(last_term[1])
                self._writer.append(last_term)
                counter += 1
                last_term = next_term
                if counter % 25000 == 0:
                    self.printer.print_merge_progress_message(counter)
        self.printer.print_end_of_merge_message(counter)
        for reader in self._readers:
            remove(reader.file_path)
        self.stats.signal_end_of_merge()
