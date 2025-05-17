# src/main.py
from src.workflow import run_workflow

def main():
    # Example natural language query
    nl_query = "Show me the top 10 countries that speak spanish along with their percentages."
    final_output = run_workflow(nl_query)
    print("Workflow completed with output:", final_output)

if __name__ == "__main__":
    main()