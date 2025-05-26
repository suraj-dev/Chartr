import plotly.express as px

def plot_data(labels, values, title="Data Visualization"):
    """
    Plots a simple bar chart given labels and values using Plotly.
    Returns the Plotly figure object for further use (display, export, etc.).
    """
    fig = px.bar(x=labels, y=values, labels={'x': 'Labels', 'y': 'Values'}, title=title)
    fig.show()
    return fig  # Optionally return the figure if you want to save/export