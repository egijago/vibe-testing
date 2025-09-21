from state.state import State, REPORTS, TERMINATION_THRESHOLD, LLM_CALL_COUNT, NODE_NAME

class FlowEvaluator:
    def __init__(self, max_cfg_refiner_call, max_missing_line_refiner_call): 
        self.max_cfg_refiner_call = max_cfg_refiner_call
        self.max_missing_line_refiner_call = max_missing_line_refiner_call

    def __call__(self, state: State):
        coverage = state[REPORTS][-1]
        threshold = state[TERMINATION_THRESHOLD]
        llm_call_count = state[LLM_CALL_COUNT]
        if coverage >= threshold or llm_call_count >= 1 + self.max_missing_line_refiner_call + self.max_cfg_refiner_call: 
            return "test_completer"
        if llm_call_count >= 1 + self.max_missing_line_refiner_call: 
            return "test_refiner_cfg"
        else: 
            return "test_refiner_missing_line"
    
