from langgraph.graph import StateGraph
from plotly.graph_objects import Figure
from src.query import extract_db_schema, run_nl_to_sql_with_verification
from src.db import get_connection
from src.types import WorkflowState
from src.visualize import get_chart_type, plot_data
from src.observability import tracer


def convert_nl_to_sql(state: WorkflowState):
    with tracer.start_as_current_span("convert_nl_to_sql"):
        nl_query = state["nl_query"]
        sql_query = run_nl_to_sql_with_verification(nl_query)
        print("Converted NL to SQL:", sql_query)
        return {"sql_query": sql_query}


def execute_sql(state: WorkflowState):
    sql_query = state["sql_query"]
    try:
        with tracer.start_as_current_span("execute_sql"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return {"results": results, "column_names": column_names}
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return {"results": []}


def visualize_results(state: WorkflowState):
    with tracer.start_as_current_span("visualize_results"):
        results = state["results"]
        print(results)
        chart_config = state["chart_config"]
        columns = state["column_names"]
        chart = plot_data(
            results, chart_config.get("chart_type"), columns, chart_config.get("title")
        )
        return {"chart": chart}


def get_chart_recommendation(state: WorkflowState):
    with tracer.start_as_current_span("get_chart_recommendation"):
        nl_query = state["nl_query"]
        sql_query = state["sql_query"]
        chart_config = get_chart_type(nl_query, sql_query, extract_db_schema())
        return {"chart_config": chart_config}


def create_workflow():
    graph = StateGraph(WorkflowState)

    graph.add_node("convert_nl_to_sql", convert_nl_to_sql)
    graph.add_node("execute_sql", execute_sql)
    graph.add_node("recommend_chart_type", get_chart_recommendation)
    graph.add_node("visualize_results", visualize_results)

    graph.set_entry_point("convert_nl_to_sql")
    graph.add_edge("convert_nl_to_sql", "execute_sql")
    graph.add_edge("execute_sql", "recommend_chart_type")
    graph.add_edge("recommend_chart_type", "visualize_results")

    return graph.compile()


def run_workflow(nl_query) -> Figure:
    with tracer.start_as_current_span("run_workflow"):
        graph = create_workflow()
        initial_state = {"nl_query": nl_query}
        result = graph.invoke(initial_state)
        return result["chart"]
