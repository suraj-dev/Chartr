import json
import plotly.express as px

from src.query import get_openai_client
from src.types import ChartConfig

def get_chart_type(nl_query: str, sql_query: str, schema: str) -> ChartConfig:
    prompt = (
        f"""
        You are a data visualization expert.
        Given the following user query: '{nl_query}'
        And the corresponding SQL query: '{sql_query}'
        And the db schema: {schema}
        Suggest the most suitable Plotly chart type (bar, line, pie, scatter, histogram).
        Recommend the X axis and Y axis labels.
        Also, recommend the title for the chart.
        Return the output as a json object with keys: chart_type, x_label, y_label, and title.
        Return only the JSON object and nothing more.
        """
    )
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o",  # or your local LLM's name
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    print(f"Chart config: {response.choices[0].message.content}")
    chart_config = json.loads(response.choices[0].message.content)
    return chart_config


def plot_data(data: list, chart_type: str, columns: list, title="Data Visualization"):
    """
    Plot data using Plotly based on chart_type.
    :param chart_type: Chart type string (e.g., 'bar', 'line', etc.)
    :param data: List of tuples from SQL results
    :param columns: List of column names
    :param title: Chart title
    """
    # Convert list of tuples and columns to dicts for Plotly
    data_dict = {col: [row[idx] for row in data] for idx, col in enumerate(columns)}

    match chart_type:
        case "bar":
            fig = px.bar(data_dict, x=columns[0], y=columns[1], title=title)
        case "line":
            fig = px.line(data_dict, x=columns[0], y=columns[1], title=title)
        case "scatter":
            fig = px.scatter(data_dict, x=columns[0], y=columns[1], title=title)
        case "pie":
            fig = px.pie(data_dict, names=columns[0], values=columns[1], title=title)
        case "histogram":
            fig = px.histogram(data_dict, x=columns[0], title=title)
        case _:
            raise ValueError(f"Unsupported chart type: {chart_type}")

    fig.show()
    return fig