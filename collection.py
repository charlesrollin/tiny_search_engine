import glob
from threading import Lock

from utils import save_map
from printer import CollectionPrinter


class Document(object):

    def __init__(self, doc_id):
        self.doc_id = doc_id

    def getText(self, id_storer):
        result = list()
        doc_path = id_storer.doc_map[self.doc_id]
        with open(doc_path) as doc_file:
            for line in doc_file:
                result += line.split()
        return result


class Block(object):

    def __init__(self, block_path, id_storer):
        self.block_path = block_path
        documents = glob.glob(block_path + "/*")
        self.documents = list()
        for document in documents:
            self.documents.append(id_storer.add_doc(document))

    def __len__(self):
        return len(self.documents)


class Collection(object):

    def __init__(self, collection_path, verbose):
        self.printer = CollectionPrinter(verbose)
        self.printer.print_build_collection_start_message(collection_path)
        self.collection_path = collection_path
        self.id_storer = IDStorer()
        self.blocks = [Block(path, self.id_storer) for path in glob.glob(collection_path + "/*")]
        self.printer.print_build_end_message(len(self.blocks), len(self))

    def store_maps(self):
        save_map(self.id_storer.doc_map, "indexes/" + self.collection_path + "/docmap")
        save_map(self.id_storer.term_map, "indexes/" + self.collection_path + "/termmap")

    def __len__(self):
        return self.id_storer.get_doc_counter()


class IDStorer(object):

    def __init__(self):
        self._doc_counter = 0
        self._term_counter = 0
        self.doc_map = dict()
        self.term_map = dict()
        self.lock = Lock()

    def get_doc_counter(self):
        return self._doc_counter

    def add_doc(self, doc_path):
        self._doc_counter += 1
        self.doc_map[self._doc_counter] = doc_path
        return self._doc_counter

    def add_term(self, term):
        with self.lock:
            self._term_counter += 1
            self.term_map[term] = self._term_counter
            return self._term_counter

    def get_term_id(self, term):
        with self.lock:
            if term in self.term_map:
                return self.term_map[term]
            self._term_counter += 1
            self.term_map[term] = self._term_counter
            return self._term_counter

