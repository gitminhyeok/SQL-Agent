from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents.state import AgentState
from agents.nodes import (
    retrieve_context_node,
    generate_sql_node,
    execute_sql_node,
    analyze_result_node
)


def build_graph():
    """bulid workflow"""
    print("building workflow..")
    memory = MemorySaver()

    workflow = StateGraph(AgentState)

    workflow.add_node("retriever", retrieve_context_node)
    workflow.add_node("generator", generate_sql_node)
    workflow.add_node("executor", execute_sql_node)
    
    workflow.set_entry_point("retriever")

    workflow.add_edge("retriever", "generator")

    # 추후 HITL 적용
    workflow.add_edge("generator", "executor")

    # workflow.add_conditional_edges()
    
    workflow.add_edge("generator", END)

    app = workflow.compile(
        checkpointer=memory,
        interrupt_before=["executor"]  # executor 노드 진입 전 실행 중단
    )

    return app

if __name__ == "__main__":
    app = build_graph()
    print(app)