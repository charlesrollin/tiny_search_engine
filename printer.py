class ConsolePrinter(object):

    def __init__(self, verbose=True):
        self.verbose = verbose

    def _validate_print(self, msg):
        if self.verbose:
            print(msg)


class ParsePrinter(ConsolePrinter):

    def print_block_parse_start_message(self, nb_blocks):
        self._validate_print("Starting parse of %i blocks" % nb_blocks)

    def print_block_parse_end_message(self, blocks_left):
        self._validate_print("\tIn progress:  %i blocks parsed" % blocks_left)


class MergePrinter(ConsolePrinter):

    def print_merge_start_message(self):
        self._validate_print("Merging block indexes...")

    def print_merge_progress_message(self, counter):
        self._validate_print("\t%i terms processed" % counter)

    def print_end_of_merge_message(self, counter):
        self._validate_print("Merging ended: %i unique terms found" % counter)


class QueryParserPrinter(ConsolePrinter):

    def print_results(self, sub_results, total_results, time):
        if self.verbose:
            print("%i documents found in %.2f seconds" % (total_results, time))
            print("Printing first %i documents" % len(sub_results))
            for doc in sub_results:
                print("\t%.5f: %s" % (doc[1], doc[0]))


class TestPrinter(ConsolePrinter):

    def print_test_progress(self, counter, tot):
        self._validate_print("Testing weight function %i out of %i" % (counter, tot))


class CollectionPrinter(ConsolePrinter):

    def print_build_collection_start_message(self, collection_path):
        self._validate_print("Building collection %s..." % collection_path)

    def print_build_end_message(self, blocks_amount, doc_counter):
        if self.verbose:
            print("\t- %s blocks detected" % blocks_amount)
            print("\t- %s documents detected" % doc_counter)
