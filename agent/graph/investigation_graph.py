"""LangGraph investigation state machine."""

from langgraph.graph import StateGraph, END
from agent.graph.state import InvestigationState
from agent.graph.nodes.context_fetch import fetch_context
from agent.graph.nodes.historical_retrieval import retrieve_historical
from agent.graph.nodes.hypothesis_generation import generate_hypotheses
from agent.graph.nodes.evidence_collection import collect_evidence
from agent.graph.nodes.external_intelligence import fetch_external_intelligence
from agent.graph.nodes.evidence_synthesis import synthesize_evidence
from agent.graph.nodes.rca_narrative import generate_rca_narrative
from agent.graph.nodes.nba_recommendations import generate_recommendations
from agent.graph.nodes.output_serialization import serialize_output


def build_investigation_graph() -> StateGraph:
    graph = StateGraph(InvestigationState)

    graph.add_node("fetch_context", fetch_context)
    graph.add_node("retrieve_historical", retrieve_historical)
    graph.add_node("generate_hypotheses", generate_hypotheses)
    graph.add_node("collect_evidence", collect_evidence)
    graph.add_node("fetch_external_intelligence", fetch_external_intelligence)
    graph.add_node("synthesize_evidence", synthesize_evidence)
    graph.add_node("generate_rca_narrative", generate_rca_narrative)
    graph.add_node("generate_recommendations", generate_recommendations)
    graph.add_node("serialize_output", serialize_output)

    graph.set_entry_point("fetch_context")
    graph.add_edge("fetch_context", "retrieve_historical")
    graph.add_edge("retrieve_historical", "generate_hypotheses")
    graph.add_edge("generate_hypotheses", "collect_evidence")
    graph.add_edge("collect_evidence", "fetch_external_intelligence")
    graph.add_edge("fetch_external_intelligence", "synthesize_evidence")
    graph.add_edge("synthesize_evidence", "generate_rca_narrative")
    graph.add_edge("generate_rca_narrative", "generate_recommendations")
    graph.add_edge("generate_recommendations", "serialize_output")
    graph.add_edge("serialize_output", END)

    return graph.compile()


INVESTIGATION_GRAPH = build_investigation_graph()
