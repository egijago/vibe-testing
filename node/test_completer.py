from state.state import State, VERIFIED_TESTS, SOURCE_CODE, OUTPUT_DIR, MODULE_NAME, NODE_NAME
from typing import List 
from pathlib import Path
from math import inf


class TestCompleter:
    def __call__(self, state: State):
        verified_tests = state[VERIFIED_TESTS]
        function_code   = state[SOURCE_CODE]
        out_dir     = Path(state[OUTPUT_DIR])
        module_name = state[MODULE_NAME]

        pytest_code = self.make_pytest_module(function_code, verified_tests)
        out_dir.mkdir(parents=True, exist_ok=True)
        file_path = out_dir / f"test_{module_name}.py"

        import_string = f"from source.{module_name} import *\n"
        pytest_code = self.make_pytest_module(function_code, verified_tests, import_string)
        file_path.write_text(pytest_code, encoding="utf-8")
        return {NODE_NAME: self.__class__.__name__}
    
    def make_pytest_module(self, function_code: str, generated_calls: List[str], import_str: str = "") -> str:
        namespace = {}
        try:
            exec(function_code, namespace)
        except Exception as e:
            raise RuntimeError(f"Failed to execute function_code: {type(e).__name__}: {e}") from e

        tests: List[str] = []
        needs_pytest = False
        inf_found = False

        for i, call in enumerate(generated_calls):
            call_str = call.strip()
            try:
                value = eval(call_str, namespace)
                if abs(value) == inf:
                    inf_found = True
                tests.append(
                    f"def test_{i}():\n"
                    f"    assert {call_str} == {repr(value)}\n"
                )
            except Exception as e:
                needs_pytest = True
                exc_name = type(e).__name__
                tests.append(
                    f"def test_{i}():\n"
                    f"    with pytest.raises({exc_name}):\n"
                    f"        {call_str}\n"
                )

        header = "from math import inf\n" if inf_found else ""
        header += f"import pytest\n{import_str}\n\n" if needs_pytest else f"{import_str}\n\n"
         
        return header + "\n".join(tests)