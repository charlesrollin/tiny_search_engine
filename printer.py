class ConsolePrinter(object):

    def __init__(self, verbose=True):
        self.verbose = verbose

    def _validate_print(self, msg):
        if self.verbose:
            print(msg)


class ParsePrinter(ConsolePrinter):

    def print_block_parse_start_message(self, block_path):
        self._validate_print("Parsing block %s" % block_path)

    def print_block_parse_end_message(self, block_path):
        self._validate_print("Block %s successfully parsed" % block_path)


class MergePrinter(ConsolePrinter):

    def print_merge_start_message(self):
        self._validate_print("Merging block indexes...")

    def print_merge_progress_message(self, counter):
        self._validate_print("\t%i terms processed" % counter)

    def print_end_of_merge_message(self, counter):
        self._validate_print("Merging ended: %i unique terms found" % counter)


class RefinePrinter(ConsolePrinter):

    def print_refine_start_message(self):
        self._validate_print("Refining index")

    def print_refine_progress_message(self, counter):
        self._validate_print("\t%i terms refined" % counter)

    def print_end_of_refine_message(self):
        self._validate_print("Refine ended")


class QueryParserPrinter(ConsolePrinter):

    def print_results(self, sub_results, total_results):
        if self.verbose:
            print("Printing first %i documents out of %i" % (len(sub_results), total_results))
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
