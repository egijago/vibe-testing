from state.state import State, SOURCE_CODE, CODE_PROCESSOR, COVERED_LINES, MESSAGES, GENERATED_TESTS, LLM_CALL_COUNT, NUM_TEST_GENERATED, NODE_NAME, CFG_SYSTEM_MSG_FLAG
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
import re

class TestRefinerMissingLine: 
    def __init__(self, llm):
        self.llm = llm
    
    def __call__(self, state: State) -> dict:
        source_code = state[SOURCE_CODE]
        code_processor = state[CODE_PROCESSOR]
        covered_lines = state[COVERED_LINES]
        messages = state[MESSAGES]
        llm_call_count = state[LLM_CALL_COUNT]
        missing_lines = set(code_processor.statements) - set(covered_lines) 
        function_name = code_processor.function_name 
        messages, result = self.refine_test_cases(messages, source_code, missing_lines, function_name)


        return {NODE_NAME: self.__class__.__name__, GENERATED_TESTS: result, MESSAGES: messages,  LLM_CALL_COUNT: llm_call_count + 1, NUM_TEST_GENERATED: state[NUM_TEST_GENERATED] + len(result)}

    def refine_test_cases(self, messages, source_code: str, missing_lines: list, function_name: str):
        user_prompt = f"""\
Your previous attempt to generate function calls failed to achieve 100% coverage. Your new task is to generate *only the additional* function calls needed to cover the specific lines of code that were missed.

**Function Source Code:**
{source_code}

**Coverage Report:**
The following lines were NOT covered by the previous set of calls:
{missing_lines}

**Instructions (Revised):**
1.  **Reasoning ([THINKING]):** Analyze each uncovered line number provided. For each one, explain the exact condition needed to execute it and construct a new, specific function call that meets that condition.
2.  **New Function Calls ([CODE]):** For **each** uncovered line, generate **up to 3 new function calls** to ensure it is covered. Each call must follow this exact format: `{function_name}([unique_value_for_path_n])`. Do not include any previously generated calls."""
        messages.append(HumanMessage(content=user_prompt))
        response = self.llm.invoke(messages)
        messages.append(AIMessage(content=response.content))
        
        return messages, self.get_function_call(function_name, response.content)
    
    def get_function_call(self, function_name, text):
        pattern = re.compile(rf'\b{re.escape(function_name)}\s*\([^()]*\)')
        matches = pattern.findall(text)
        return list(set(matches)) 
    

class TestRefinerCFG: 
    def __init__(self, llm):
        self.llm = llm
    
    def __call__(self, state: State) -> dict:
        source_code = state[SOURCE_CODE]
        code_processor = state[CODE_PROCESSOR]
        covered_lines = state[COVERED_LINES]
        messages = state[MESSAGES]
        llm_call_count = state[LLM_CALL_COUNT]
        flag = state[CFG_SYSTEM_MSG_FLAG]

        missing_lines = set(code_processor.statements) - set(covered_lines) 
        function_name = code_processor.function_name 

        code_processor.compute_path_to_line_numbers(list(missing_lines))
        paths = []
        for line in list(missing_lines):
            path = code_processor.path_to_code_lines_map.get(line)
            if path:
                paths.append(path)

        exec_paths = []
        for path in paths: 
            exec_path = code_processor.path_to_code_lines_refiner(path)
            exec_paths.append(exec_path)

        messages, result = self.refine_test_cases(messages, source_code, exec_paths, function_name, flag, missing_lines)

        return {NODE_NAME: self.__class__.__name__, GENERATED_TESTS: result, MESSAGES: messages,  LLM_CALL_COUNT: llm_call_count + 1, NUM_TEST_GENERATED: state[NUM_TEST_GENERATED] + len(result), CFG_SYSTEM_MSG_FLAG: True}

    def refine_test_cases(self, messages, source_code: str, paths: list, function_name: str, flag:bool, missing_line):
        user_prompt = f"""\
Your previous attempt to generate function calls did not achieve full coverage.
Your new task is to generate additional function calls that specifically exercise EACH missing execution path in the program.
Here are the uncovered lines that must be addressed:
{list(missing_line)}

#### Input Data

**1. Source Code:**
```python
{source_code}
```

**2. Execution Paths:**

"""     
        formatted_path = []
        for i, path in enumerate(paths): 
            formatted_path += [f"""\
* **Path {i}:**
    ```
{path}
    ```
"""]    
        user_prompt += "\n".join(formatted_path)
        
        if not flag: 
            system_prompt = """\
**Role:** You are an expert software tester and code analyst. Your task is to generate a set of unique, precise inputs for a given function. Each input will force the program to follow a specific execution path from a provided list of paths.

**Instructions:**

Your goal is to produce a distinct test case for each execution_path provided in the input data. Iterate through the list of paths and perform the following steps for each one:
1. **Analyze the Code and Path:** Carefully examine the provided source_code and the current execution_path. The path is a sequence of line numbers that must be executed in order.
2. **Determine Conditional Outcomes:** For each if statement encountered in the execution_path, determine if its condition must evaluate to True or False to allow execution to proceed to the next line in the path. Explain your reasoning.
3. **Derive Input Constraints:** Based on your analysis for the current path, consolidate all conditions into a final set of mathematical constraints that the input variable must satisfy.
4. **Generate a Unique Test Case:** Provide a single, concrete input value that meets all the derived constraints. This value must be different from any test cases generated for the other paths.

**Required Output Format:**

For each path, generate a distinct section with the following structure.

---
### Path 0 Analysis

#### 1. Path Analysis
* **Line [number]:** `if (condition)` must be **[True/False]**. [Reasoning].
* **Line [number]:** `if (condition)` must be **[True/False]**. [Reasoning].

#### 2. Derived Constraints on `[variable]`
* [List of constraints for this path]
* **Combined constraint:** [Final combined constraint for this path]

#### 3. Generated Test Case
* `[variable] = [unique_value_for_path_0]`

#### 4. Function Call
```python
[function_name]([unique_value_for_path_0])
```
---
### Path 1 Analysis

#### 1. Path Analysis
* **Line [number]:** `if (condition)` must be **[True/False]**. [Reasoning].
* ...

#### 2. Derived Constraints on `[variable]`
* ...

#### 3. Generated Test Case
* `[variable] = [unique_value_for_path_1]`

#### 4. Function Call
```python
[function_name]([unique_value_for_path_1])
```
---
*(...continue for all other paths)*
"""
            messages.append(SystemMessage(content=system_prompt)) 

        messages.append(HumanMessage(content=user_prompt))
        response = self.llm.invoke(messages)
        messages.append(AIMessage(content=response.content))
        
        return messages, self.get_function_call(function_name=function_name, text=response.content)
    
    def get_function_call(self, function_name, text):
        pattern = re.compile(rf'\b{re.escape(function_name)}\s*\([^()]*\)')
        matches = pattern.findall(text)
        return list(set(matches)) 
