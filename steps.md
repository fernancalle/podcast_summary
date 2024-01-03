# Podcast Transcription Pipeline - Step-by-Step Guide

## Overview

This guide outlines the setup and operational steps for the Podcast Transcription Pipeline using Apache Airflow 2.7.x. This pipeline automates downloading, transcribing, and storing podcast episodes in a SQLite database.

## 1: Setting Up Airflow

### Installation
- **Create a Virtual Environment**: Recommended for managing dependencies.
- **Install Airflow 2.7.x**:
    ```bash
    python --version  # Confirm Python 3.8+
    CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-2.7.x/constraints-3.8.txt"
    pip install "apache-airflow==2.7.x" --constraint "${CONSTRAINT_URL}"
    ```
- **Initialize Airflow**:
    - Execute `airflow db init` to initialize the Airflow database.
    - Start the Airflow web server with `airflow webserver` and the scheduler with `airflow scheduler` in separate terminals.

### Airflow Configuration
- Adjust the `airflow.cfg` file to point to your DAGs directory.

## 2: Writing the DAG

### DAG Setup
- Import necessary modules: `xmltodict`, `requests`, `pandas`, `vosk`, `pydub`, etc.
- Define constants: `PODCAST_URL`, `EPISODE_FOLDER`, `FRAME_RATE`.
- Configure the DAG:
    ```python
    from airflow.decorators import dag, task
    from airflow.utils.dates import days_ago

    @dag(
        dag_id='podcast_summary',
        default_args={
            'owner': 'airflow',
            'start_date': days_ago(1)
        },
        catchup=False
    )
    def podcast_summary():
        create_database = create_database_task()
        podcast_episodes = get_podcast_episodes_task()
        new_episodes = load_new_episodes_task(podcast_episodes)
        processed_episodes = process_audio_and_generate_transcripts(new_episodes)
        filtered_episodes = filter_episodes(processed_episodes, criteria={})
        
        create_database >> podcast_episodes >> new_episodes >> processed_episodes >> filtered_episodes
    ```

### Task Definitions
- **Create Database Task**: SQL setup for SQLite database and execution with `SqliteOperator`.
- **Podcast Metadata Processing**: Fetching and parsing data using `requests` and `xmltodict`.
- **Audio File Downloading**: Logic for downloading episodes.
- **Audio Transcription**: Transcribing audio using `vosk` and updating the database.
- **Episode Filtering (Optional)**: Filtering logic based on specified criteria.

## 3: Executing the Pipeline

- Start the Airflow web server and scheduler.
- Place the `podcast_summary.py` script in the Airflow DAGs folder.
- Trigger and monitor the pipeline via the Airflow web interface.

## 4: Future Extensions

- Implement complex filtering or integrate additional data sources.
- Enhance database schema for detailed metadata storage.
- Explore advanced audio processing or machine learning models.
