import matplotlib.pyplot as plt
import pandas as pd

def plot_benchmark_results(results_list: list):
    """
    Plots a list of benchmark result dictionaries and returns the figure.
    """
    df_all = pd.DataFrame(results_list)
    
    # Create a 2x2 subplot grid
    fig, ax = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('CQC vs. SQL Benchmark Comparison', fontsize=16)

    # Plot 1: Execution Time
    df_all.plot(kind='bar', x='query_expr', y='execution_time_seconds', ax=ax[0, 0], legend=False, color=['#1f77b4', '#ff7f0e'])
    ax[0, 0].set_title('Execution Time')
    ax[0, 0].set_ylabel('Time (seconds)')
    ax[0, 0].set_xlabel('')
    ax[0, 0].tick_params(axis='x', rotation=0)

    # Plot 2: Peak Memory Usage
    df_all.plot(kind='bar', x='query_expr', y='memory_peak_bytes', ax=ax[0, 1], legend=False, color=['#2ca02c', '#d62728'])
    ax[0, 1].set_title('Peak Memory Usage')
    ax[0, 1].set_ylabel('Memory (bytes)')
    ax[0, 1].set_xlabel('')
    ax[0, 1].tick_params(axis='x', rotation=0)

    # Plot 3: Result Rows
    df_all.plot(kind='bar', x='query_expr', y='result_rows', ax=ax[1, 0], legend=False, color=['#9467bd', '#8c564b'])
    ax[1, 0].set_title('Number of Result Rows')
    ax[1, 0].set_ylabel('Row Count')
    ax[1, 0].set_xlabel('')
    ax[1, 0].tick_params(axis='x', rotation=0)

    # Plot 4: Result Columns
    df_all.plot(kind='bar', x='query_expr', y='result_columns', ax=ax[1, 1], legend=False, color=['#e377c2', '#7f7f7f'])
    ax[1, 1].set_title('Number of Result Columns')
    ax[1, 1].set_ylabel('Column Count')
    ax[1, 1].set_xlabel('')
    ax[1, 1].tick_params(axis='x', rotation=0)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # Instead of plt.show(), return the figure object
    return fig
