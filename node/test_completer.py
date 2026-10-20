from state.state import State, VERIFIED_TESTS, SOURCE_CODE, OUTPUT_DIR, MODULE_NAME, NODE_NAME
from typing import List 
from pathlib import Path
from sandbox.executor import LocalExecutor


class TestCompleter:
    def __init__(self, executor=None):
        self.executor = executor or LocalExecutor()

    def __call__(self, state: State):
        verified_tests = state[VERIFIED_TESTS]
        function_code   = state[SOURCE_CODE]
        out_dir     = Path(state[OUTPUT_DIR])
        module_name = state[MODULE_NAME]

        out_dir.mkdir(parents=True, exist_ok=True)
        file_path = out_dir / f"test_{module_name}.py"

        import_string = f"from source.{module_name} import *\n"
        pytest_code = self.make_pytest_module(function_code, verified_tests, import_string)
        file_path.write_text(pytest_code, encoding="utf-8")
        return {NODE_NAME: self.__class__.__name__}
    
    def make_pytest_module(self, function_code: str, generated_calls: List[str], import_str: str = "") -> str:
        results = self.executor.evaluate_calls(function_code, generated_calls)

        tests: List[str] = []
        needs_pytest = False
        inf_found = False

        for i, (call, result) in enumerate(zip(generated_calls, results)):
            call_str = call.strip()
            if result["ok"]:
                if result["inf"]:
                    inf_found = True
                tests.append(
                    f"def test_{i}():\n"
                    f"    assert {call_str} == {result['repr']}\n"
                )
            else:
                needs_pytest = True
                exc_name = result["exc_name"]
                tests.append(
                    f"def test_{i}():\n"
                    f"    with pytest.raises({exc_name}):\n"
                    f"        {call_str}\n"
                )

        header = "from math import inf\n" if inf_found else ""
        header += f"import pytest\n{import_str}\n\n" if needs_pytest else f"{import_str}\n\n"
         
        return header + "\n".join(tests)