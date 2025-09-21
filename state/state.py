from __future__ import annotations
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from state.code_processor import CodeProcessor


SOURCE_CODE = "source_code"
GENERATED_TESTS = "generated_tests"
VERIFIED_TESTS = "verified_tests" 
MESSAGES = "messages"
CODE_PROCESSOR = "code_processor"
REPORTS = "reports"
OUTPUT_DIR = "output_dir"
MODULE_NAME = "module_name"
COVERED_LINES = "covered_lines"
TERMINATION_THRESHOLD = "termination_threshold"
LLM_CALL_COUNT = "llm_call_count"
NUM_TEST_GENERATED = "num_test_generated"
NODE_NAME = "node_name"
CFG_SYSTEM_MSG_FLAG = "cfg_system_msg_flag"

class State(TypedDict): 
    source_code: str
    covered_lines: set
    generated_tests: list[str]
    verified_tests: list[str]
    code_processor: CodeProcessor
    messages: list
    coverage: list
    output_dir: str
    module_name: str
    termination_threshold: float
    llm_call_count: int
    reports: list
    num_test_generated: int
    node_name: str
    cfg_system_msg_flag: bool