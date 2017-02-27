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

    def print_results(self, results, time):
        counter = 0
        if self.verbose:
            print("%i document%s found in %.3f seconds" % (len(results), "s" if len(results) > 1 else "", time))
            while counter * 10 < len(results):
                print("Printing result page [%i/%i]" % (counter+1, len(results)//10 + (1 if len(results) % 10 != 0 else 0)))
                for i, doc in enumerate(results[10*counter:min(10*(counter+1), len(results))]):
                    print("\t%i. [%.5f]: %s" % (10*counter + i+1, doc[1], doc[0]))
                counter += 1
                if counter * 10 < len(results):
                    go_next = '?'
                    while len(go_next) == 0 or go_next[0] not in ['y', 'n']:
                        go_next = input("Go to next page? (y/n) ")
                        if len(go_next) > 0 and go_next[0] == "n":
                            print()
                            return
                else:
                    print("End of results.")
            print()

    def print_query_constraints(self):
        message = "**********" \
                  "\nBoolean queries must respect the following structure:" \
                  "\n\t- the query is written in CNF, i.e. a conjunction of disjunctions " \
                  "\n\t- disjunctions are separated with the && (AND) operator " \
                  "\n\t- a disjunction is a list of terms separated with the || (OR) operator and surrounded with parenthesis " \
                  "Two extra rules ensure that queries are well-defined: " \
                  "\n\t- the NOT operator can only apply to a disjunction (and not to a term) " \
                  "\n\t\t--> (foobar) && !(foo || bar) is well-defined " \
                  "\n\t\t--> (foobar) && (!foo || bar) is not (cf. end of doc) " \
                  "\n\t- the query must contain at least one not-negated disjunction " \
                  "\n\t\t--> (foobar) && !(foo || bar) is well-defined " \
                  "\n\t\t--> !(foo || bar) is not (cf. end of doc)" \
                  "\n**********"
        self._validate_print(message)


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
