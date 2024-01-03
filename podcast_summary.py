import os
import json
import requests
import xmltodict
import logging
from datetime import datetime
from airflow.decorators import dag, task
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.providers.sqlite.hooks.sqlite import SqliteHook
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment

# Constants and Configuration
PODCAST_URL = "https://www.marketplace.org/feed/podcast/marketplace/"
EPISODE_FOLDER = "episodes"
FRAME_RATE = 16000

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# DAG configuration
@dag(
    dag_id='podcast_summary',
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
)
def podcast_summary():
    start_task = DummyOperator(task_id='start')
    create_database = create_database_task()
    podcast_episodes = get_podcast_episodes_task()
    new_episodes = load_new_episodes_task(podcast_episodes)
    processed_episodes = process_audio_and_generate_transcripts(new_episodes)
    filtered_episodes = filter_episodes(processed_episodes, criteria={})  # Define criteria here
    end_task = DummyOperator(task_id='end')

    start_task >> create_database >> podcast_episodes >> new_episodes >> processed_episodes >> filtered_episodes >> end_task

# Task to create database
def create_database_task():
    sql_command = '''
    CREATE TABLE IF NOT EXISTS episodes (
        link TEXT PRIMARY KEY,
        title TEXT,
        filename TEXT,
        published TEXT,
        description TEXT,
        transcript TEXT
    );
    '''
    return SqliteOperator(
        task_id='create_table_sqlite',
        sql=sql_command,
        sqlite_conn_id="podcasts"
    )

# Task to get podcast episodes
@task()
def get_podcast_episodes_task():
    try:
        response = requests.get(PODCAST_URL)
        response.raise_for_status()  # Raises an HTTPError for bad requests
        feed = xmltodict.parse(response.text)
        episodes = feed["rss"]["channel"]["item"]
        logging.info(f"Found {len(episodes)} episodes.")
        return episodes
    except requests.HTTPError as e:
        logging.error(f"HTTP Error: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        return []

# Task to load new episodes into the database
@task()
def load_new_episodes_task(episodes):
    hook = SqliteHook(sqlite_conn_id="podcasts")
    stored_episodes_query = "SELECT * from episodes;"
    stored_episodes = hook.get_pandas_df(stored_episodes_query)
    new_episodes = []

    for episode in episodes:
        if episode["link"] not in stored_episodes["link"].values:
            filename = f"{episode['link'].split('/')[-1]}.mp3"
            new_episode_data = [
                episode["link"],
                episode["title"],
                episode["pubDate"],
                episode["description"],
                filename
            ]
            new_episodes.append(new_episode_data)

    if new_episodes:
        hook.insert_rows(table='episodes',
                         rows=new_episodes,
                         target_fields=["link", "title", "published", "description", "filename"])
        logging.info(f"Loaded {len(new_episodes)} new episodes into the database.")
    else:
        logging.info("No new episodes to load.")

    return new_episodes

# Function to process audio files and generate transcripts (example of added functionality)
@task()
def process_audio_and_generate_transcripts(episodes):
    model = Model("model_path")  # Path to the vosk model directory
    for episode in episodes:
        audio_file_path = os.path.join(EPISODE_FOLDER, episode['filename'])
        audio = AudioSegment.from_mp3(audio_file_path)
        audio = audio.set_frame_rate(FRAME_RATE)

        recognizer = KaldiRecognizer(model, FRAME_RATE)
        transcript = ""
        with open(audio_file_path, 'rb') as audio_file:
            while True:
                data = audio_file.read(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    transcript += result.get("text", "") + " "
        
        # Update the database with the transcript
        update_transcript_in_database(episode['link'], transcript)

    return episodes

# Function to update the database with the transcript
def update_transcript_in_database(episode_link, transcript):
    update_query = "UPDATE episodes SET transcript = ? WHERE link = ?"
    hook = SqliteHook(sqlite_conn_id="podcasts")
    hook.run(update_query, parameters=(transcript, episode_link))