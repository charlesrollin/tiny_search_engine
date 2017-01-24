from evaluation.testing import TestBuilder


def run_test(collection_path, queries_file_path, results_file_path):
    # type: (str, str, str) -> None
    tb = TestBuilder(queries_file_path, results_file_path)
    tb.test(collection_path)
