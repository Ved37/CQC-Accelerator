# CQC-Accelerator

An interactive framework for optimizing, visualizing, and analyzing Conjunctive Queries with Comparisons (CQCs). This project aims to provide a user-friendly GUI and efficient query processing for relational and graph-structured data, supporting analytical and machine learning workloads.

## Overview

CQC-Accelerator bridges theoretical advancements in query optimization with practical, user-friendly systems. It is designed for students, analysts, and researchers working with large relational datasets. The system includes modules for query formulation, visualization, efficient evaluation, and integration with real-world use cases like ML feature extraction and graph pattern matching.

## Modules

- **Core CQC Engine**: Runs queries efficiently using reduction techniques and constant-delay enumeration.
- **Visual Optimizer**: Displays join trees and comparison graphs, highlighting short/long comparisons.
- **GUI Interface**: Allows users to build and run queries interactively using Streamlit.
- **ML Feature Extractor**: Uses query output as features in machine learning models.
- **Graph Pattern Matcher**: Encodes patterns (e.g., triangles) as CQCs and runs them on graph data.
- **Benchmarking Suite**: Compares performance of CQCs vs. traditional SQL queries.

## Technology Stack

- **Primary Language**: Python
- **GUI Framework**: Streamlit
- **Data Processing**: Pandas, Matplotlib, Numpy
- **Database Backend**: SQLite (initial), Spark (for scaling)
- **ML Integration**: Scikit-learn

## Project Structure

```
CQC-Accelerator/
├── core_engine/              # Core query processing and optimization
├── visual_optimizer/         # Visualization of query structures
├── gui_interface/            # Streamlit-based user interface
├── ml_feature_extractor/     # ML feature extraction from query outputs
├── graph_pattern_matcher/    # Graph pattern analysis using CQCs
├── benchmarking_suite/       # Performance comparison tools
├── data/                     # Datasets and schemas for testing
├── docs/                     # Documentation and user guides
└── requirements.txt          # Project dependencies
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd CQC-Accelerator
   ```
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the Streamlit GUI:
   ```
   streamlit run gui_interface/app.py
   ```

## Contribution Guidelines

This project is developed by a team of 7 members. We use Git for version control with a Git Flow branching strategy. Please follow these steps:

- Create a feature branch for your work (`feature/<module-name>`).
- Submit pull requests for review before merging to `develop`.
- Ensure code quality through testing and documentation.

## License

To be determined.

## Acknowledgments

Inspired by the work of Qichen Wang and Ke Yi on Conjunctive Queries with Comparisons (SIGMOD 2022).
