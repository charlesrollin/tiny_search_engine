from queue import Queue
from os import remove

from utils import file_line_to_term_index, term_index_to_file_line
from printer import MergePrinter


class BlockIndexReader(object):
    """
    An implementation of a reading queue with a fixed capacity.
    """

    def __init__(self, file_path, capacity):
        self._position = 0
        self.file_path = file_path
        self._read_buffer = Queue(capacity)  # Using thread-safe object while not in multi-thread environment...
        self._fill_queue()

    def _fill_queue(self):
        if self._read_buffer.empty():
            with open(self.file_path) as block_index_file:
                block_index_file.seek(self._position)
                while not self._read_buffer.full():
                    new_line = block_index_file.readline()
                    if new_line == "":
                        break
                    self._read_buffer.put(file_line_to_term_index(new_line))
                self._position = block_index_file.tell()

    def pop(self):
        result = self._read_buffer.get()
        if self._read_buffer.empty():
            self._fill_queue()
        return result

    def peek(self):
        if self._read_buffer.empty():
            return None
        return self._read_buffer.queue[0]


class BlockIndexMerger(object):

    def __init__(self, collection, stats, total_capacity, verbose):
        self._collection = collection
        self._readers = list()
        self._capacity = total_capacity / (len(collection.blocks) + 1)
        for block in collection.blocks:
            self._readers.append(BlockIndexReader("indexes/" + block.block_path, self._capacity))
        self._write_buffer = list()
        self.stats = stats
        self.printer = MergePrinter(verbose)

    def _flush(self):
        with open("indexes/" + self._collection.collection_path + ".index", "a") as index_file:
            for term_index in self._write_buffer:
                self.stats.process_posting_list(term_index[1])
                index_file.write(term_index_to_file_line(term_index))
        self._write_buffer = list()

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
        try:
            remove("indexes/" + self._collection.collection_path + ".index")
        except OSError:
            pass
        self.printer.print_merge_start_message()
        counter = 0
        last_term = self._get_lexically_first()
        while last_term is not None:
            next_term = self._get_lexically_first()
            if next_term is not None and last_term[0] == next_term[0]:
                last_term = last_term[0], (last_term[1] + next_term[1])
            else:
                self._write_buffer.append(last_term)
                counter += 1
                last_term = next_term
                if counter % 25000 == 0:
                    self.printer.print_merge_progress_message(counter)
                if len(self._write_buffer) == self._capacity:
                    self._flush()
        self.printer.print_end_of_merge_message(counter)
        for reader in self._readers:
            remove(reader.file_path)
        self.stats.signal_end_of_merge()
