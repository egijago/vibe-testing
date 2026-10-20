from graph.graph import build_graph
from sandbox.executor import make_executor
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from pathlib import Path
import json
from datetime import datetime, timezone
import argparse  # Import the argparse library

# A whitelist of keys to include in the state when logging.
WHITELIST_KEYS = {
    "node_name", "covered_lines", "num_test_generated", "llm_call_count",
    "reports", "messages", "generated_tests", "verified_tests"
}

def sanitize_state(state: dict) -> dict:
    """Filters the state dictionary to include only whitelisted keys for logging."""
    return {k: v for k, v in state.items() if k in WHITELIST_KEYS}

class EnhancedJSONEncoder(json.JSONEncoder):
    """
    A custom JSON encoder that handles sets and objects with a to_dict method.
    """
    def default(self, o):
        if isinstance(o, set):
            return list(o)
        if hasattr(o, "to_dict"):
            return o.to_dict()
        try:
            return vars(o)
        except Exception:
            return repr(o)

def get_initial_state(source_code, output_dir, module_name, termination_threshold=100):
    """Creates the initial state dictionary for the graph execution."""
    return {
        "source_code": source_code,
        "generated_tests": [],
        "verified_tests": [],
        "code_processor": None,
        "messages": [],
        "reports": [],
        "output_dir": str(output_dir),
        "module_name": module_name,
        "termination_threshold": termination_threshold,
        "llm_call_count": 0,
        "covered_lines": set(),
        "num_test_generated": 0,
        "cfg_system_msg_flag": False
    }

def main(source_dir_path: str, output_dir_path: str, model: str, mlr: int, cr: int,
         executor: str = "exec", sandbox_image: str = "vibe-testing-sandbox:latest",
         sandbox_timeout: float = 30, sandbox_runtime: str = None):
    """
    Main function to process source files in a directory and generate tests.

    Args:
        source_dir_path: The path to the directory containing source code.
        output_dir_path: The path to the directory where outputs will be saved.
        model: The language model to use.
        mlr: The value for MLR.
        cr: The value for CR.
        executor: Where to run generated code: "exec" (in-process) or "docker" (sandboxed container).
        sandbox_image: Docker image used when executor is "docker".
        sandbox_timeout: Per-execution timeout in seconds when executor is "docker".
        sandbox_runtime: Optional Docker runtime (e.g. "runsc" for gVisor) when executor is "docker".
    """

    load_dotenv()

    # Initialize the language model and the graph
    llm = init_chat_model(f"openai:{model}")
    code_executor = make_executor(executor, image=sandbox_image, timeout=sandbox_timeout, runtime_name=sandbox_runtime)
    graph = build_graph(llm, mlr, cr, code_executor)

    # Define source and output directories from arguments
    source_dir = Path(source_dir_path)
    output_dir = Path(output_dir_path)
    log_dir = output_dir / "log"

    # Ensure output and log directories exist
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create a blacklist of already processed files to avoid re-running
    blacklist = set([file.name[5:] for file in output_dir.glob("*.py")])
    print(f"Already implemented test cases: {len(blacklist)}")

    # Iterate over all Python files in the source directory
    for file in source_dir.glob("*.py"):
        if file.name == "__init__.py":
            continue

        if file.name in blacklist:
            print(f"Skipping already processed file: {file.name}")
            continue

        module_name = file.stem
        print(f"Processing {module_name}")

        with file.open("r", encoding="utf-8") as f:
            source_code = f.read()

        initial_state = get_initial_state(source_code, output_dir, module_name)

        log_file = log_dir / f"{module_name}.jsonl"
        step = 0
        final_coverage = None

        # Stream the graph execution and log each step
        with log_file.open("w", encoding="utf-8") as f:
            for snapshot in graph.stream(initial_state, stream_mode="values"):
                record = {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "module_name": module_name,
                    "step": step,
                    "state": sanitize_state(snapshot),
                }
                f.write(json.dumps(record, cls=EnhancedJSONEncoder) + "\n")
                step += 1
                if snapshot["reports"]:
                    final_coverage = snapshot["reports"][-1]

        if final_coverage:
            print(f"Final coverage for {module_name}: {final_coverage}")
        else:
            print(f"No coverage report generated for {module_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate tests for Python source files.")
    parser.add_argument("--output_dir", required=True, help="The directory to save output files and logs.")
    parser.add_argument("--source_dir", required=True, help="The directory containing the source code files.")
    parser.add_argument("--model", default="gpt-4o", help="The language model to use (default: gpt-4o).")
    parser.add_argument("--mlr", type=int, default=2, help="The maximum call of missing line refiner (integer).")
    parser.add_argument("--cr", type=int, default=2, help="The maximum call of cfg refiner (integer).")
    parser.add_argument("--executor", choices=["exec", "docker"], default="exec",
                        help="Where to execute source/generated code: 'exec' runs in-process (default), 'docker' runs in a sandboxed container.")
    parser.add_argument("--sandbox_image", default="vibe-testing-sandbox:latest", help="Docker image for --executor docker.")
    parser.add_argument("--sandbox_timeout", type=float, default=30, help="Per-execution timeout in seconds for --executor docker.")
    parser.add_argument("--sandbox_runtime", default=None, help="Optional Docker runtime for --executor docker, e.g. 'runsc' (gVisor).")


    args = parser.parse_args()

    main(
        source_dir_path=args.source_dir,
        output_dir_path=args.output_dir,
        model=args.model,
        mlr=args.mlr,
        cr=args.cr,
        executor=args.executor,
        sandbox_image=args.sandbox_image,
        sandbox_timeout=args.sandbox_timeout,
        sandbox_runtime=args.sandbox_runtime,
    )
