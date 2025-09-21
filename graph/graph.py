from langgraph.graph import StateGraph, START, END
from state.state import State
from node.test_generator import TestGeneratorCFG, TestGeneratorExhaustive
from node.test_runner import TestRunner
from node.test_completer import TestCompleter
from node.test_refiner import TestRefinerMissingLine, TestRefinerCFG
from node.flow_evaluator import FlowEvaluator


def build_graph(llm, max_missing_line_refiner_call, max_cfg_refiner_call):
    graph_builder = StateGraph(State)
    graph_builder.add_node(
        "test_generator",
        TestGeneratorExhaustive(llm),
    )
    graph_builder.add_node(
        "test_runner",
        TestRunner(),
    )
    graph_builder.add_node(
        "test_refiner_missing_line",
        TestRefinerMissingLine(llm),
    )
    graph_builder.add_node(
        "test_refiner_cfg",
        TestRefinerCFG(llm),
    )

    graph_builder.add_node(
        "test_completer", 
        TestCompleter()
    )
    
    graph_builder.set_entry_point("test_generator")  
    graph_builder.add_edge("test_generator", "test_runner")
    graph_builder.add_conditional_edges(
    "test_runner",
    FlowEvaluator(max_missing_line_refiner_call=max_missing_line_refiner_call, max_cfg_refiner_call=max_cfg_refiner_call),
    {
        "test_completer": "test_completer",
        "test_refiner_cfg": "test_refiner_cfg",
        "test_refiner_missing_line": "test_refiner_missing_line"
    }
    )
    graph_builder.add_edge("test_refiner_cfg", "test_runner")
    graph_builder.add_edge("test_refiner_missing_line", "test_runner")
    graph_builder.set_finish_point("test_completer")


    return graph_builder.compile()
