from queue import Queue

from os import remove

from utils import file_line_to_term_index, term_index_to_file_line


class SequentialIndexReader(object):
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
            with open(self.file_path) as index_file:
                index_file.seek(self._position)
                while not self._read_buffer.full():
                    new_line = index_file.readline()
                    if new_line == "":
                        break
                    self._read_buffer.put(file_line_to_term_index(new_line))
                self._position = index_file.tell()

    def pop(self):
        result = self._read_buffer.get()
        if self._read_buffer.empty():
            self._fill_queue()
        return result

    def peek(self):
        if self._read_buffer.empty():
            return None
        return self._read_buffer.queue[0]


class SequentialIndexWriter(object):
    """
    An implementation of a writing queue with a fixed capacity.
    """

    def __init__(self, file_path, capacity, refined=False):
        self.file_path = file_path
        self._write_buffer = list()
        self._refined = refined
        self.capacity = capacity
        self.positions = dict()
        try:  # because of the append mode, we first try to delete the existing file
            remove(file_path)
        except OSError:
            pass

    def _flush(self):
        with open(self.file_path, 'a') as index_file:
            for term_index in self._write_buffer:
                if self._refined:
                    self.positions[term_index[0]] = index_file.tell()
                index_file.write(term_index_to_file_line(term_index))
        self._write_buffer = list()

    def append(self, term_index):
        self._write_buffer.append(term_index)
        if len(self._write_buffer) >= self.capacity:
            self._flush()

    def close(self):
        self._flush()
