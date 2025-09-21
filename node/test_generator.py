from state.state import State, GENERATED_TESTS, SOURCE_CODE, CODE_PROCESSOR, MESSAGES, LLM_CALL_COUNT, NUM_TEST_GENERATED, NODE_NAME, CFG_SYSTEM_MSG_FLAG
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
import re
from state.code_processor import CodeProcessor

class TestGeneratorCFG:
    def __init__(self, llm):
        self.llm = llm 

    def __call__(self, state: State):                
        source_code = state[SOURCE_CODE]
        code_processor = CodeProcessor()
        code_processor.build_from_source(source_code)
        llm_call_count = state[LLM_CALL_COUNT]

        execution_paths = code_processor.find_all_execution_path()
        execution_paths = code_processor.remove_redundant_line_coverage_path(execution_paths)
        execution_paths_str = code_processor.paths_to_code_lines(execution_paths)
        messages, result = self.generate_test_cases(source_code=source_code, paths=execution_paths_str, function_name=code_processor.function_name)
        
        return {NODE_NAME: self.__class__.__name__, CODE_PROCESSOR: code_processor, GENERATED_TESTS: result, MESSAGES: messages, LLM_CALL_COUNT: llm_call_count + 1, NUM_TEST_GENERATED: state[NUM_TEST_GENERATED] + len(result), CFG_SYSTEM_MSG_FLAG: True}

    def generate_test_cases(self, source_code: str, paths: list[str], function_name) -> list[str]:
        system_prompt = """\
You are an expert software tester and code analyst. Your task is to generate a set of unique, precise inputs for a given function. Each input will force the program to follow a specific execution path from a provided list of paths.

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

        user_prompt = f"""\
This is the concrete data for a specific task that you would provide to the system-prompted LLM.

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
                
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self.llm.invoke(messages)
        messages += [AIMessage(content=response.content)]
        
        return messages, self.get_function_call(function_name=function_name, text=response.content)
    
    def get_function_call(self, function_name, text):
        pattern = re.compile(rf'\b{re.escape(function_name)}\s*\([^()]*\)')
        matches = pattern.findall(text)
        return list(set(matches)) 
    
class TestGeneratorExhaustive:
    def __init__(self, llm):
        self.llm = llm 

    def __call__(self, state: State):                
        source_code = state[SOURCE_CODE]
        code_processor = CodeProcessor()
        code_processor.build_from_source(source_code)
        llm_call_count = state[LLM_CALL_COUNT]

        messages, result = self.generate_test_cases(source_code=source_code, function_name=code_processor.function_name)
        
        return {NODE_NAME: self.__class__.__name__, CODE_PROCESSOR: code_processor, GENERATED_TESTS: result, MESSAGES: messages,  LLM_CALL_COUNT: llm_call_count + 1, NUM_TEST_GENERATED: state[NUM_TEST_GENERATED] + len(result)}

    def generate_test_cases(self, source_code: str, function_name) -> list[str]:
        system_prompt = """\
You are an expert Python software tester specializing in automated software testing. Your primary goal is to analyze Python functions and devise a diverse set of function calls to achieve 100% line coverage.

You think systematically, identifying all execution paths, including:
- Conditional branches (`if`/`elif`/`else`)
- Loops (`for`/`while`)
- Error handling (`try`/`except`)
- Edge cases (`None`, 0, empty values, negative numbers)

Your output format is strict: first, provide your reasoning in a `[THINKING]` block, and then provide only the executable code in a `[CODE]` block."""

        user_prompt = f"""\
Your task is to generate a set of Python function calls for the function provided below.

**Function Source Code:**
{source_code}

**Instructions:**
1.  **Reasoning ([THINKING]):** First, detail your thought process. Map every execution path (if/else, loops, exceptions) to a specific input value. State explicitly which line number(s) each input is designed to cover.
2.  **Function Calls ([CODE]):** Second, list the Python function calls you designed. Provide only the calls, one per line, using this exact format: `{function_name}(params...)`."""  
               
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self.llm.invoke(messages)
        messages += [AIMessage(content=response.content)]
        
        return messages, self.get_function_call(function_name=function_name, text=response.content)
    
    def get_function_call(self, function_name, text):
        pattern = re.compile(rf'\b{re.escape(function_name)}\s*\([^()]*\)')
        matches = pattern.findall(text)
        return list(set(matches)) 