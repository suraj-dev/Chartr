from typing import TypedDict

class ChartConfig(TypedDict):
    chart_type: str
    x_label: str
    y_label: str
    title: str

class WorkflowState(TypedDict):
    nl_query: str
    sql_query: str
    results: list
    column_names: list
    chart_config: ChartConfig