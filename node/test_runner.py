from state.state import State, GENERATED_TESTS, VERIFIED_TESTS, SOURCE_CODE, REPORTS, COVERED_LINES, CODE_PROCESSOR, NODE_NAME
import os
import sys
import runpy
import tempfile
from typing import List
from coverage import Coverage


class TestRunner:
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
        """
        Run `source_code` under coverage while evaluating each expression in `call_strings`.
        Returns the sorted list of line numbers in the source that were executed.

        - call_strings are evaluated with the module's globals (so "foo(1)" works if foo is defined).
        - Exceptions raised by any call are caught so the rest still run.
        - Requires `coverage` package (coverage.py).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            src_path  = os.path.join(tmpdir, "src_module.py")
            test_path = os.path.join(tmpdir, "test_module.py")

            with open(src_path, "w", encoding="utf-8") as f:
                f.write(source_code)

            calls_literal = ", ".join(repr(s) for s in call_strings)
            test_code = f"""\
import importlib

m = importlib.import_module("src_module")

_calls = [{calls_literal}]

for _expr in _calls:
    try:
        eval(_expr, m.__dict__, {{}})
    except Exception:
        pass"""
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(test_code)

            # Make the temp dir importable
            sys.path.insert(0, tmpdir)
            try:
                # Ensure a fresh import of src_module
                sys.modules.pop("src_module", None)

                cov = Coverage(branch=False, source=[tmpdir])  # only measure files in tmpdir
                cov.start()                                    # start BEFORE running the test file
                runpy.run_path(test_path, run_name="__main__")
                cov.stop(); cov.save()

                # Compute covered = statements - missing for the source file
                _, statements, _excluded, missing, _percent = cov.analysis2(src_path)
                covered = sorted(set(statements) - set(missing))
                return covered
            finally:
                # Clean sys.path even if something fails
                if sys.path and sys.path[0] == tmpdir:
                    sys.path.pop(0)