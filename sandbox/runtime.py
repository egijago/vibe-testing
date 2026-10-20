import os
import re
import sys
import json
import runpy
import tempfile
from typing import List
from coverage import Coverage


def statement_lines(source_code: str) -> List[int]:
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "snippet.py")
        with open(path, "w") as f:
            f.write(source_code)

        cov = Coverage()
        cov.start()
        runpy.run_path(path, run_name="__main__")  # run the file
        cov.stop(); cov.save()

        filename, statements, excluded, missing, output = cov.analysis2(path)
        return statements


def covered_lines(source_code: str, call_strings: List[str]) -> List[int]:
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

        sys.path.insert(0, tmpdir)
        try:
            sys.modules.pop("src_module", None)

            cov = Coverage(branch=False, source=[tmpdir])
            cov.start()
            runpy.run_path(test_path, run_name="__main__")
            cov.stop(); cov.save()

            _, statements, _excluded, missing, _percent = cov.analysis2(src_path)
            covered = sorted(set(statements) - set(missing))
            return covered
        finally:
            # Clean sys.path even if something fails
            if sys.path and sys.path[0] == tmpdir:
                sys.path.pop(0)


def evaluate_calls(source_code: str, call_strings: List[str]) -> List[dict]:
    namespace = {}
    try:
        exec(source_code, namespace)
    except Exception as e:
        raise RuntimeError(f"Failed to execute function_code: {type(e).__name__}: {e}") from e

    results = []
    for call in call_strings:
        try:
            value = eval(call.strip(), namespace)
        except Exception as e:
            results.append({"ok": False, "exc_name": type(e).__name__})
            continue
        value_repr = repr(value)
        results.append({"ok": True, "repr": value_repr, "inf": bool(re.search(r"\binf\b", value_repr))})
    return results


OPS = {
    "statement_lines": lambda job: statement_lines(job["source_code"]),
    "covered_lines": lambda job: covered_lines(job["source_code"], job["calls"]),
    "evaluate_calls": lambda job: evaluate_calls(job["source_code"], job["calls"]),
}


def _worker_main():
    # Keep a private handle on the real stdout for the JSON result, and point fd 1 at
    # stderr so anything the executed code prints wont corrupt the json.
    result_out = os.fdopen(os.dup(1), "w", encoding="utf-8")
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    worker_pid = os.getpid()

    try:
        job = json.load(sys.stdin)
        response = {"ok": True, "result": OPS[job["op"]](job)}
    except BaseException as e:
        response = {"ok": False, "error": f"{type(e).__name__}: {e}"}

    if os.getpid() != worker_pid:
        os._exit(0)
    result_out.write(json.dumps(response))
    result_out.flush()


if __name__ == "__main__":
    _worker_main()
