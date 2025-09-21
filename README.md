This tool leverages Large Language Models (LLMs) and a graph-based workflow powered by LangChain to automatically generate unit tests for Python source code. It iteratively analyzes code, generates tests, and refines them to improve coverage.

***

## ✨ Features

* **🤖 AI-Powered Test Generation**: Uses language models like GPT-4o to write meaningful tests for your Python files.
* **📈 Coverage-Driven Refinement**: The system tracks code coverage and iteratively refines tests to cover more lines.
* **⚙️ Configurable Workflow**: Easily adjust parameters like the AI model and the number of refinement steps.
* **📝 Detailed Logging**: Each step of the generation process is logged to a `.jsonl` file for easy debugging and inspection.
* **⏩ Smart Processing**: Automatically skips files that already have generated tests, saving time and resources on subsequent runs.

***


## 🚀 Getting Started

Follow these steps to set up and run the test generator.

**Note**: It's highly recommended to run this in a container or virtualized environment because it executes code directly from an LLM.

---

### Prerequisites

* Python 3.8+
* An OpenAI API key

### Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/egijago/vibe-testing
    cd vibe-testing
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**:
    First, ensure you have Graphviz installed on your system.

    For Windows users: You may need to set environment variables so pip can find your Graphviz installation. Open a Command Prompt and run the following, adjusting the path if necessary:
    ```
    set GRAPHVIZ_DIR=C:\Program Files\Graphviz
    set INCLUDE=%GRAPHVIZ_DIR%\include;%INCLUDE%
    set LIB=%GRAPHVIZ_DIR%\lib;%LIB%
    ```
    Next, install the required Python packages using the requirements.txt file.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file in the root of the project and add your OpenAI API key.

    **`.env`**:
    ```
    OPENAI_API_KEY="your-api-key-here"
    ```

***

## 💻 Usage

Run the script from your terminal, specifying the source code directory and the output directory for the generated tests.

After the program halts, you can examine the log using the log reader, `reader.html`.

### Command

```bash
python main.py --source_dir <path_to_your_code> --output_dir <path_for_generated_tests> [options]
```

| Argument | Description | Default |
| :--- | :--- | :--- |
| **`--source_dir`** | (**Required**) The path to the folder containing the Python files you want to test. | `None` |
| **`--output_dir`** | (**Required**) The path to the folder where the generated tests and logs will be saved. | `None` |
| **`--model`** | The specific AI model to use for test generation (e.g., `gpt-4o`, `gpt-3.5-turbo`). | `gpt-4o` |
| **`--mlr`** | Sets the maximum number of times the tool will try to refine tests to cover missing lines. | `2` |
| **`--cr`** | Sets the maximum number of times the tool will try to refine tests by analyzing the code's control flow. | `2` |