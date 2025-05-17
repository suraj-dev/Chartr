import matplotlib.pyplot as plt

def plot_data(labels, values, title="Data Visualization"):
    """Plots a simple bar chart given labels and values."""
    plt.figure(figsize=(8, 6))
    plt.bar(labels, values)
    plt.xlabel("Labels")
    plt.ylabel("Values")
    plt.title(title)
    plt.show()