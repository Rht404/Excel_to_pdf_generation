# from typing import Dict, Any, List
# import os
# from crewai import Agent, Task, Crew, Process
# from crewai.tools import tool
# from pathlib import Path
# from agents.data_agent import DataAgent
# from agents.insight_agent import InsightAgent
# from agents.viz_agent import VizAgent
# from agents.report_agent import ReportAgent
# from dotenv import load_dotenv
# import truststore

# # Ensure system truststore is injected for SSL
# truststore.inject_into_ssl()

# # Load environment variables from .env
# load_dotenv(Path(__file__).parent / ".env")

# from crewai import LLM

# # Initialize LLM with Azure OpenAI credentials
# llm = LLM(
#     model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     base_url=os.getenv("AZURE_OPENAI_BASE"),
# )

# # Instantiate agents
# data_agent = DataAgent()
# insight_agent = InsightAgent()
# viz_agent = VizAgent()
# report_agent = ReportAgent()

# # ----------------------
# # Tools
# # ----------------------
# @tool("extract_and_summarize_data")
# def extract_and_summarize_data(file_path: str) -> Dict[str, Any]:
#     """Read an Excel file and return a structured per-sheet summary dict."""
#     return data_agent.process(file_path)


# @tool("generate_data_insights")
# def generate_data_insights(summary: Dict[str, Any], **kwargs) -> Dict[str, str]:
#     """Generate sheet-wise bullet insights using the LLM."""
#     return insight_agent.generate_insights(summary)


# @tool("generate_chart_plan")
# def generate_chart_plan(summary: Dict[str, Any]) -> dict:
#     """Generate chart plan JSON from summary."""
#     return insight_agent.generate_chart_plan(summary)


# @tool("create_visualizations")
# def create_visualizations(summary: Dict[str, Any], chart_plan: dict = None, **kwargs) -> Dict[str, List[Dict[str, str]]]:
#     """Create charts for each sheet using raw dataframes and the chart plan."""
#     dataframes = summary.get("dataframes") or {}
#     return viz_agent.create_charts(summary, dataframes, chart_plan)


# @tool("generate_exec_summary")
# def generate_exec_summary(summary: Dict[str, Any]) -> str:
#     """Generate executive summary text from summary."""
#     return insight_agent.generate_exec_summary(summary)


# @tool("generate_business_insights")
# def generate_business_insights(summary: Dict[str, Any]) -> Dict[str, str]:
#     """Generate business insights per sheet."""
#     return insight_agent.generate_business_insights(summary)


# @tool("generate_pdf_report")
# def generate_pdf_report(summary: Dict[str, Any],
#                         insights: Dict[str, str] | None,
#                         charts: Dict[str, List[Dict[str, str]]] | None,
#                         executive_summary: str | None = None,
#                         business_insights: Dict[str, str] | None = None) -> str:
#     """Assemble the final PDF report from summary, insights, charts, exec summary, and business insights."""
#     insights = insights or {}
#     charts = charts or {}
#     executive_summary = executive_summary or ""
#     business_insights = business_insights or {}
#     return report_agent.generate_pdf(summary, insights, charts, executive_summary, business_insights)

# # ----------------------
# # Agents
# # ----------------------
# data_expert = Agent(
#     role="Data Analyst",
#     goal="Summarize the uploaded Excel file into structured, sheet-wise summaries.",
#     backstory="You carefully inspect data to extract its structure, missingness, and key statistics.",
#     llm=llm,
#     tools=[extract_and_summarize_data],
#     allow_delegation=False,
#     verbose=True,
# )

# insight_expert = Agent(
#     role="Insight Strategist",
#     goal="Derive clear numeric and categorical insights from structured summaries.",
#     backstory="You are skilled at finding patterns, anomalies, correlations, and key narratives in datasets.",
#     llm=llm,
#     tools=[generate_data_insights, generate_chart_plan, generate_exec_summary, generate_business_insights],
#     allow_delegation=False,
#     verbose=True,
# )

# viz_expert = Agent(
#     role="Visualization Engineer",
#     goal="Transform summarized data into clear charts.",
#     backstory="You specialize in converting data into visuals like histograms, bar charts, and heatmaps.",
#     llm=llm,
#     tools=[create_visualizations],
#     allow_delegation=False,
#     verbose=True,
# )

# report_expert = Agent(
#     role="Report Composer",
#     goal="Combine insights, visuals, and summaries into a professional PDF report.",
#     backstory="You assemble analytical results into a clear, structured, well-formatted PDF.",
#     llm=llm,
#     tools=[generate_pdf_report],
#     allow_delegation=False,
#     verbose=True,
# )

# # ----------------------
# # Tasks
# # ----------------------
# load_task = Task(
#     description="Summarize Excel via extract_and_summarize_data.",
#     expected_output="summary dict",
#     agent=data_expert,
#     tools=[extract_and_summarize_data],
# )

# insight_task = Task(
#     description="Generate sheet-wise insights via generate_data_insights.",
#     expected_output="insights dict",
#     agent=insight_expert,
#     tools=[generate_data_insights],
# )

# chart_plan_task = Task(
#     description="Generate chart plan via generate_chart_plan.",
#     expected_output="chart plan dict",
#     agent=insight_expert,
#     tools=[generate_chart_plan],
# )

# viz_task = Task(
#     description="Create charts via create_visualizations.",
#     expected_output="charts dict",
#     agent=viz_expert,
#     tools=[create_visualizations],
# )

# exec_summary_task = Task(
#     description="Generate executive summary via generate_exec_summary.",
#     expected_output="executive summary string",
#     agent=insight_expert,
#     tools=[generate_exec_summary],
# )

# business_insights_task = Task(
#     description="Generate business insights via generate_business_insights.",
#     expected_output="business insights dict",
#     agent=insight_expert,
#     tools=[generate_business_insights],
# )

# report_task = Task(
#     description="Assemble PDF via generate_pdf_report.",
#     expected_output="pdf path",
#     agent=report_expert,
#     tools=[generate_pdf_report],
#     inputs={
#         "summary": load_task,
#         "insights": insight_task,
#         "charts": viz_task,
#         "executive_summary": exec_summary_task,
#         "business_insights": business_insights_task,
#     },
# )

# # ----------------------
# # Pipeline Runner
# # ----------------------
# def run_pipeline(file_path: str) -> str:
#     crew = Crew(
#         agents=[data_expert, insight_expert, viz_expert, report_expert],
#         tasks=[load_task, insight_task, chart_plan_task, viz_task,
#                exec_summary_task, business_insights_task, report_task],
#         process=Process.sequential,
#         verbose=True,
#     )

#     result = crew.kickoff(inputs={"file_path": file_path})
#     return result





# # pipeline.py — LangGraph version
# from typing import TypedDict, Optional, Dict, Any, List

# from langgraph.graph import StateGraph, START, END

# from agents.data_agent import DataAgent
# from agents.insight_agent import InsightAgent
# from agents.viz_agent import VizAgent
# from agents.report_agent import ReportAgent


# # ----------------------
# # State schema
# # ----------------------
# class PipelineState(TypedDict, total=False):
#     file_path: str
#     summary: Dict[str, Any]
#     insights: Dict[str, str]
#     chart_plan: Dict[str, Any]
#     charts: Dict[str, List[Dict[str, str]]]
#     exec_summary: str
#     business_insights: Dict[str, str]
#     pdf_path: str
#     error: Optional[str]


# # ----------------------
# # Agents (reused exactly as you built them — no changes needed inside these classes)
# # ----------------------
# data_agent = DataAgent()
# insight_agent = InsightAgent()
# viz_agent = VizAgent()
# report_agent = ReportAgent()


# # ----------------------
# # Nodes
# # ----------------------
# def load_node(state: PipelineState) -> dict:
#     summary = data_agent.process(state["file_path"])
#     return {"summary": summary}


# def insights_node(state: PipelineState) -> dict:
#     return {"insights": insight_agent.generate_insights(state["summary"])}


# def chart_plan_node(state: PipelineState) -> dict:
#     try:
#         plan = insight_agent.generate_chart_plan(state["summary"])
#     except Exception as e:
#         print(f"[chart_plan_node] falling back to empty plan: {e}")
#         plan = {}
#     return {"chart_plan": plan}


# def exec_summary_node(state: PipelineState) -> dict:
#     return {"exec_summary": insight_agent.generate_exec_summary(state["summary"])}


# def business_insights_node(state: PipelineState) -> dict:
#     return {"business_insights": insight_agent.generate_business_insights(state["summary"])}


# def viz_node(state: PipelineState) -> dict:
#     dataframes = state["summary"].get("dataframes") or {}
#     charts = viz_agent.create_charts(state["summary"], dataframes, state.get("chart_plan") or {})
#     return {"charts": charts}


# def report_node(state: PipelineState) -> dict:
#     pdf_path = report_agent.generate_pdf(
#         state["summary"],
#         state.get("insights") or {},
#         state.get("charts") or {},
#         state.get("exec_summary") or "",
#         state.get("business_insights") or {},
#     )
#     return {"pdf_path": str(pdf_path)}


# # ----------------------
# # Graph wiring
# # ----------------------
# graph = StateGraph(PipelineState)

# graph.add_node("load", load_node)
# graph.add_node("insights", insights_node)
# graph.add_node("chart_plan", chart_plan_node)
# graph.add_node("exec_summary", exec_summary_node)
# graph.add_node("business_insights", business_insights_node)
# graph.add_node("viz", viz_node)
# graph.add_node("report", report_node)

# graph.add_edge(START, "load")

# # Fan-out: these four only need `summary`, so LangGraph runs them concurrently
# for node_name in ["insights", "chart_plan", "exec_summary", "business_insights"]:
#     graph.add_edge("load", node_name)

# # viz only needs the chart_plan, not the other three branches
# graph.add_edge("chart_plan", "viz")

# # Fan-in: report waits until all four branches complete
# for node_name in ["insights", "viz", "exec_summary", "business_insights"]:
#     graph.add_edge(node_name, "report")

# graph.add_edge("report", END)

# compiled_graph = graph.compile()


# # ----------------------
# # Public entrypoint — same signature as before, main.py needs no changes
# # ----------------------
# def run_pipeline(file_path: str) -> str:
#     result = compiled_graph.invoke({"file_path": file_path})
#     return result["pdf_path"]




# pipeline.py — LangGraph version (serialized LLM calls for local Ollama)
# pipeline.py
import matplotlib
matplotlib.use("Agg")  # set before agents are imported

from typing import TypedDict, Optional, Dict, Any, List
from langgraph.graph import StateGraph, START, END

from agents.data_agent import DataAgent
# ... rest of pipeline.py unchanged
from agents.insight_agent import InsightAgent
from agents.viz_agent import VizAgent
from agents.report_agent import ReportAgent


# ----------------------
# State schema
# ----------------------
class PipelineState(TypedDict, total=False):
    file_path: str
    summary: Dict[str, Any]
    insights: Dict[str, str]
    chart_plan: Dict[str, Any]
    charts: Dict[str, List[Dict[str, str]]]
    exec_summary: str
    business_insights: Dict[str, str]
    pdf_path: str
    error: Optional[str]


# ----------------------
# Agents
# ----------------------
data_agent = DataAgent()
insight_agent = InsightAgent()
viz_agent = VizAgent()
report_agent = ReportAgent()


# ----------------------
# Nodes
# ----------------------
def load_node(state: PipelineState) -> dict:
    summary = data_agent.process(state["file_path"])
    return {"summary": summary}


def insights_node(state: PipelineState) -> dict:
    return {"insights": insight_agent.generate_insights(state["summary"])}


def chart_plan_node(state: PipelineState) -> dict:
    try:
        plan = insight_agent.generate_chart_plan(state["summary"])
    except Exception as e:
        print(f"[chart_plan_node] falling back to empty plan: {e}")
        plan = {}
    return {"chart_plan": plan}


def exec_summary_node(state: PipelineState) -> dict:
    return {"exec_summary": insight_agent.generate_exec_summary(state["summary"])}


def business_insights_node(state: PipelineState) -> dict:
    return {"business_insights": insight_agent.generate_business_insights(state["summary"])}


def viz_node(state: PipelineState) -> dict:
    dataframes = state["summary"].get("dataframes") or {}
    charts = viz_agent.create_charts(state["summary"], dataframes, state.get("chart_plan") or {})
    return {"charts": charts}


def report_node(state: PipelineState) -> dict:
    pdf_path = report_agent.generate_pdf(
        state["summary"],
        state.get("insights") or {},
        state.get("charts") or {},
        state.get("exec_summary") or "",
        state.get("business_insights") or {},
    )
    return {"pdf_path": str(pdf_path)}


# ----------------------
# Graph wiring — fully serial for LLM-dependent nodes
# ----------------------
# NOTE: earlier version fanned out insights / chart_plan / exec_summary /
# business_insights in parallel. That's the right shape for a hosted API that
# truly serves concurrent requests, but a local Ollama instance processes one
# generation at a time — parallel calls just queue behind each other and time
# out. So this version runs LLM calls one after another. viz still only
# depends on chart_plan, so it doesn't need to wait for the other three.
graph = StateGraph(PipelineState)

graph.add_node("load", load_node)
graph.add_node("insights", insights_node)
graph.add_node("chart_plan", chart_plan_node)
graph.add_node("exec_summary", exec_summary_node)
graph.add_node("business_insights", business_insights_node)
graph.add_node("viz", viz_node)
graph.add_node("report", report_node)

graph.add_edge(START, "load")
graph.add_edge("load", "insights")
graph.add_edge("insights", "chart_plan")
graph.add_edge("chart_plan", "viz")
graph.add_edge("chart_plan", "exec_summary")
graph.add_edge("exec_summary", "business_insights")

# report waits for both remaining branches: viz and business_insights
graph.add_edge("viz", "report")
graph.add_edge("business_insights", "report")

graph.add_edge("report", END)

compiled_graph = graph.compile()


# ----------------------
# Public entrypoint
# ----------------------
def run_pipeline(file_path: str) -> str:
    result = compiled_graph.invoke({"file_path": file_path})
    return result["pdf_path"]