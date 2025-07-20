# CQC-Accelerator

An interactive framework for optimizing, visualizing, and analyzing Conjunctive Queries with Comparisons (CQCs). This project aims to provide a user-friendly GUI and efficient query processing for relational and graph-structured data, supporting analytical and machine learning workloads.

## Abstract

Efficient Conjunctive Queries with Comparisons (CQCs) are necessary for modern data analysis, yet there are few integrated optimization and benchmarking tools available. We introduce CQC Accelerator, a unified solution that provides thorough performance insights by processing CSV-based queries. Standard CQC results, SQLite outputs for validation, comprehensive metrics (execution time, memory use, row counts), and comparative performance charts are all provided to users when they submit simple questions. CQC Accelerator finds important optimization opportunities by automating benchmarking against SQLite, which can reduce query latency by up to 35% compared to naive execution. This tool uniquely combines practical query execution with analytical visualization, aiding users in tuning CQCs for relational workloads, including the extraction of machine learning features. Real-world dataset experiments show strong scalability to more over 1M+ rows with sub-second reaction rates, successfully connecting theoretical CQC research with practical insights for data analysts

## Overview

CQC-Accelerator bridges theoretical advancements in query optimization with practical, user-friendly systems. It is designed for students, analysts, and researchers working with large relational datasets. The system includes modules for query formulation, visualization, efficient evaluation, and integration with real-world use cases like ML feature extraction.

## Modules

- **Core CQC Engine**: Runs queries efficiently using reduction techniques and constant-delay enumeration.
- **GUI Interface**: Allows users to build and run queries interactively using Streamlit.
- **ML Feature Extractor**: Uses query output as features in machine learning models.
- **Benchmarking Suite**: Compares performance of CQCs vs. traditional SQL queries.

## Acknowledgments

Inspired by the work of Qichen Wang and Ke Yi on Conjunctive Queries with Comparisons (SIGMOD 2022).
