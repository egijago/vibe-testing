# VibeTesting: An Agentic AI Framework for Automated Test Case Generation

VibeTesting is an automated software testing tool that generate regeression tests based on the given python programs. It leverages LLM to iteratively analyzes code, generates tests, and refines them to improve coverage. Our benchmark shows a high line coverage result of 99.48%, 3.75 percentage points over CodaMosa. The [architectural paper](https://egijago.github.io/vibetesting_cameraready.pdf) is presented at ICAICTA 2026.

## Method

Each source file is treated as one unit under test: the first function defined in the file. For each file the pipeline runs the following steps.

1. **Generation.** The LLM receives the function source and is asked for a set of calls intended to reach full line coverage.
2. **Execution.** Each call is executed under `coverage.py` and its covered lines are recorded. A call is kept only if it covers at least one line not covered by previously kept calls.
3. **Refinement.** If coverage is below 100%, the LLM is queried again. The first `--mlr` refinements list the uncovered line numbers. The next `--cr` refinements additionally give, for each uncovered line, the shortest path to it in the function's control-flow graph (built with `pycfg`). Each refinement is followed by step 2.
4. **Completion.** The loop stops at 100% coverage or after `1 + mlr + cr` LLM calls. The kept calls are executed once more to record their return values, and a pytest module is written. It contains one test per call, asserting either the observed return value or the observed exception type.

The resulting tests are regression tests: they record the function's current behaviour and do not check it against a specification.

**Limitations.** Function calls are extracted from the LLM response with a regular expression that does not match nested parentheses. Calls whose arguments contain parentheses, such as `f(g(1))` or `f((1, 2))`, are therefore ignored. Expected values are written using their `repr`, so return values whose `repr` is not valid Python (for example `nan` or arbitrary objects) produce tests that do not pass.

## Requirements

- Python 3.9 or later (tested with 3.13)
- Graphviz with development headers, and Python development headers (needed to build `pygraphviz`)
- An OpenAI API key
- Docker, only if the sandboxed executor is used (see [Executing generated code](#executing-generated-code))

## Installation

```bash
git clone https://github.com/egijago/vibe-testing
cd vibe-testing
```

Install the system packages. On Debian or Ubuntu:

```bash
sudo apt install graphviz libgraphviz-dev python3-dev
```

On Windows, install Graphviz and tell pip where to find it before installing the Python packages. Adjust the path if needed:

```
set GRAPHVIZ_DIR=C:\Program Files\Graphviz
set INCLUDE=%GRAPHVIZ_DIR%\include;%INCLUDE%
set LIB=%GRAPHVIZ_DIR%\lib;%LIB%
```

Then create a virtual environment and install the Python dependencies:

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your key:

```
OPENAI_API_KEY=your-api-key
```

## Usage

```bash
python main.py --source_dir <source_dir> --output_dir <output_dir> [options]
```

| Argument | Description | Default |
| :--- | :--- | :--- |
| `--source_dir` | Directory containing the Python files to test. Required. | |
| `--output_dir` | Directory for generated tests and logs. Required. | |
| `--model` | OpenAI model name. | `gpt-4o` |
| `--mlr` | Maximum number of missing-line refinements. | `2` |
| `--cr` | Maximum number of control-flow-graph refinements. | `2` |
| `--executor` | Where source code and generated calls are executed: `exec` (in-process) or `docker` (sandboxed container). | `exec` |
| `--sandbox_image` | Docker image used with `--executor docker`. | `vibe-testing-sandbox:latest` |
| `--sandbox_timeout` | Wall-clock limit in seconds for each sandboxed execution. | `30` |
| `--sandbox_runtime` | Docker runtime for sandboxed executions, for example `runsc` (gVisor). | Docker default |

For each input file `<name>.py`, the tool writes the following.

- `<output_dir>/test_<name>.py`: the generated pytest module. It imports the code under test with `from source.<name> import *`, so to run it the input files must be importable as a package named `source`.
- `<output_dir>/log/<name>.jsonl`: one record of the pipeline state per step, including prompts, responses, kept calls and coverage. Open it in `reader.html` to step through a run.

Input files that already have a `test_<name>.py` in the output directory are skipped, so an interrupted run can be resumed.

### Benchmark

`data/` contains the 69 single-function Python programs used as the benchmark. To run the pipeline on it:

```bash
python main.py --source_dir data --output_dir results --executor docker
```

## Executing generated code

**`exec` (default).** Code runs inside the tool's own Python process via `exec`, `eval` and `runpy`, exactly as in earlier versions of the tool. 

**`docker` (Recommended).** Each execution runs in an ephemeral container. The container is hardened as follows:
- no network interface (`--network none`);
- a read-only root file system, with a 64 MB writable `/tmp`;
- an unprivileged user (`nobody`), all Linux capabilities dropped, and `no-new-privileges`;
- limits of 512 MB memory (no swap), one CPU, 64 processes and 256 open files;
- a wall-clock timeout (`--sandbox_timeout`), after which the container is removed.

For stronger isolation, run the containers under gVisor with `--sandbox_runtime runsc`. That requires gVisor to be installed and registered with Docker.

Build the image once before using the Docker backend:

```bash
docker build -t vibe-testing-sandbox:latest sandbox/
```
## License

MIT. See [LICENSE](LICENSE).
