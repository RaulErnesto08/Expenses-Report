from langgraph.graph import StateGraph
from schemas.state import PipelineState
from agents.processing_agent import processing_agent
from agents.action_agent import action_agent
import graphviz

def create_expense_workflow():
    """Creates and configures the expense workflow."""
    workflow = StateGraph(PipelineState)

    # Register Agents
    workflow.add_node("Processing", processing_agent)
    workflow.add_node("Action", action_agent)
    workflow.add_node("Exit", lambda state: state)  # Exit Node

    # Define Workflow Logic
    workflow.set_entry_point("Processing")
    workflow.add_edge("Processing", "Action")
    
    workflow.add_conditional_edges(
        "Action",
        lambda state: state.get("next_step"),
        {
            "Processing": "Processing",
            "Done": "Exit"
        }
    )
    
    graph = workflow.compile()
    mermaid_format = graph.get_graph().draw_mermaid()
    
    print(mermaid_format)

    return graph
