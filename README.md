# Podcast Transcription Pipeline Project

## Overview

The Podcast Transcription Pipeline Project is a simple implementation using Apache Airflow to automate the process of downloading, transcribing, and storing podcast episodes in a SQLite database. This project showcases the practical application of Airflow in managing data workflows.

## Project Objectives

- **Automated Downloading**: Implement a data pipeline to download podcast episodes efficiently.
- **Speech-to-Text Transcription**: Utilize vosk, a speech recognition toolkit, to transcribe audio content into text.
- **Database Storage**: Store and manage the podcast metadata and transcriptions in a SQLite database for streamlined access and analysis.
- **Scalability and Extendibility**: Leverage Airflow's capabilities to scale the project and add more functionalities as required.

## Code Structure

- `podcast_summary.py`: The primary script that constructs the data pipeline using Airflow, defining various tasks for data processing and management.
- `steps.md`: Provides a comprehensive guide on the steps to set up and execute the pipeline, aligning with the updated script and project requirements.

## Local Setup and Installation

### Prerequisites

- **Python Version**: Python 3.8 or higher.
- **Required Libraries**: pandas, sqlite3, xmltodict, requests, vosk, pydub.
- **Airflow Version**: Apache Airflow 2.7.x. Installation instructions can be found in the [official Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/start/local.html).

### Configuration

- Ensure proper setup of Airflow, including the web interface accessibility via `airflow standalone`.
- Place the `podcast_summary.py` script in the Airflow DAGs folder for execution.

## Data Handling

- The data pipeline is designed to automatically fetch the latest podcast episodes.
- Transcripts generated by vosk are stored along with podcast metadata in the SQLite database.
- Users can access and query the database to retrieve specific podcast information and transcripts.

