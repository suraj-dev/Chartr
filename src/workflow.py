from langgraph.graph import StateGraph
from typing import TypedDict
from src.query import nl_to_sql
from src.db import get_connection
from src.visualize import plot_data

class WorkflowState(TypedDict):
    nl_query: str
    sql_query: str
    results: list

def convert_nl_to_sql(state: WorkflowState):
    nl_query = state["nl_query"]
    sql_query = nl_to_sql(nl_query)
    print("Converted NL to SQL:", sql_query)
    return {"sql_query": sql_query}

def execute_sql(state: WorkflowState):
    sql_query = state["sql_query"]
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return {"results": results}
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return {"results": []}

def visualize_results(state: WorkflowState):
    results = state["results"]
    print(results)
    labels = [row[0] for row in results]
    values = [row[1] for row in results]
    plot_data(labels, values)
    return {}

def create_workflow():
    graph = StateGraph(WorkflowState)

    graph.add_node("convert_nl_to_sql", convert_nl_to_sql)
    graph.add_node("execute_sql", execute_sql)
    graph.add_node("visualize_results", visualize_results)

    graph.set_entry_point("convert_nl_to_sql")
    graph.add_edge("convert_nl_to_sql", "execute_sql")
    graph.add_edge("execute_sql", "visualize_results")

    return graph.compile()

def run_workflow(nl_query):
    graph = create_workflow()
    initial_state = {"nl_query": nl_query}
    result = graph.invoke(initial_state)
    return result