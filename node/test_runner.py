from state.state import State, GENERATED_TESTS, VERIFIED_TESTS, SOURCE_CODE, REPORTS, COVERED_LINES, CODE_PROCESSOR, NODE_NAME
from typing import List
from sandbox.executor import LocalExecutor


class TestRunner:
    def __init__(self, executor=None):
        self.executor = executor or LocalExecutor()

    def __call__(self, state: State):
        source_code = state[SOURCE_CODE]
        generated_tests = state[GENERATED_TESTS]
        covered_line = state[COVERED_LINES]
        verified_tests = state[VERIFIED_TESTS]
        code_processor = state[CODE_PROCESSOR]
        reports = state[REPORTS]

        for test in generated_tests:
            pref_num_of_covered_line = len(covered_line)
            covered_line_by_test = self.covered_lines_for_calls(source_code, [test])
            
            covered_line |= set(covered_line_by_test)
            if len(covered_line) == pref_num_of_covered_line:
                continue
            verified_tests.append(test)

        generated_tests = [] # empty out the generated tests
        len_stmt = len(code_processor.statements)
        coverage_percentage = (len(covered_line) / len_stmt ) * 100 
        reports.append(coverage_percentage)
        return {NODE_NAME: self.__class__.__name__, GENERATED_TESTS: generated_tests, REPORTS: reports, VERIFIED_TESTS: verified_tests}


    def covered_lines_for_calls(self, source_code: str, call_strings: List[str]) -> List[int]:
        """Returns the sorted line numbers of `source_code` executed by evaluating `call_strings`."""
        return self.executor.covered_lines(source_code, call_strings)
