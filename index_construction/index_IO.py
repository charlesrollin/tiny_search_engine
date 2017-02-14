from collections import deque
from queue import Queue

from os import remove

from utils import term_index_to_bin, bin_to_term_index, make_dirs


class SequentialIndexReader(object):
    """
    An implementation of a reading queue with a fixed capacity.
    """

    def __init__(self, file_path, positions, capacity):
        self._positions = positions
        self.file_path = file_path
        self._read_buffer = Queue(capacity)  # Using thread-safe object while not in multi-thread environment...
        self._fill_queue()

    def _read_next_binary_list(self, file):
        current_position = self._positions.popleft()
        if len(self._positions) == 0:
            size = -1
        else:
            size = self._positions[0] - current_position
        return file.read(size)

    def _fill_queue(self):
        if self._read_buffer.empty():
            with open(self.file_path, 'rb') as index_file:
                if len(self._positions) == 0:
                    return
                index_file.seek(self._positions[0])
                while not self._read_buffer.full() and len(self._positions) > 0:
                    new_bin = self._read_next_binary_list(index_file)
                    self._read_buffer.put(bin_to_term_index(new_bin))

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
        self.capacity = capacity
        self.refined= refined
        self.positions = deque()
        try:  # because of the append mode, we first try to delete the existing file
            remove(file_path)
        except OSError:
            pass
        make_dirs(file_path)  # recursively create the dirs in path if necessary

    def _flush(self):
        with open(self.file_path, 'ab') as index_file:
            for term_index in self._write_buffer:
                self.positions.append(index_file.tell())
                index_file.write(term_index_to_bin(term_index, refined=self.refined))
        self._write_buffer = list()

    def append(self, term_index):
        self._write_buffer.append(term_index)
        if len(self._write_buffer) >= self.capacity:
            self._flush()

    def close(self):
        self._flush()
