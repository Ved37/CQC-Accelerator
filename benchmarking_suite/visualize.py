import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_benchmark_results(results_list: list):
    """
    Create visualization of benchmark results using matplotlib/seaborn.
    """
    try:
        # Create DataFrame from results
        df = pd.DataFrame(results_list)
        
        # Filter out results with errors
        df_clean = df[df['error'].isnull()].copy()
        
        if df_clean.empty:
            print("No valid benchmark results to plot")
            return None
        
        # Create subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Execution time plot
        sns.barplot(data=df_clean, x='query_expr', y='execution_time_seconds', ax=ax1)
        ax1.set_title('Execution Time Comparison')
        ax1.set_ylabel('Time (seconds)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Memory usage plot
        df_clean['memory_peak_mb'] = df_clean['memory_peak_bytes'] / (1024 * 1024)
        sns.barplot(data=df_clean, x='query_expr', y='memory_peak_mb', ax=ax2)
        ax2.set_title('Memory Usage Comparison')
        ax2.set_ylabel('Memory (MB)')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        print(f"Error creating visualization: {e}")
        return None