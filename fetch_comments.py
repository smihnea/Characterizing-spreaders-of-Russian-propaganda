import logging
import requests
import sqlite3
import json

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def load_token_from_file():
    with open('C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/token_config.json', 'r') as f:
        token_data = json.load(f)
        logging.info("Token loaded from token_config.json")
    return token_data['access_token']

def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            text TEXT,
            propaganda BOOLEAN
        )
    ''')
    conn.commit()
    return conn

# Fetch video comments
def fetch_video_comments(video_id, access_token):
    url = "https://open.tiktokapis.com/v2/research/video/comment/list/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    comments = []
    cursor = 0
    has_more = True
    while has_more:
        query_body = {
            "video_id": video_id,
            "max_count": 100,
            "cursor": cursor
        }
        query_params = {
            "fields": "id,video_id,text,like_count,reply_count,parent_comment_id,create_time"
        }
        response = requests.post(url, headers=headers, json=query_body, params=query_params).json()
        if response and 'data' in response and 'comments' in response['data']:
            comments.extend(response['data']['comments'])
            cursor = response['data'].get('cursor', 0)
            has_more = response['data'].get('has_more', False)
        else:
            has_more = False
            logging.error(f"No more data or API Request failed: {response}")
    return comments

# Save comments to db (comments2 table)
def save_comments_to_db(conn, comments, propaganda):
    cursor = conn.cursor()
    for comment in comments:
        cursor.execute('''
            INSERT INTO comments2 (video_id, text, propaganda)
            VALUES (?, ?, ?)
        ''', (
            comment['video_id'], 
            comment['text'], 
            propaganda
        ))
    conn.commit()
    cursor.close()

def get_video_ids_from_db(conn, limit=100):
    cursor = conn.cursor()

    # Get 100 videos with propaganda = 1
    cursor.execute('''
        SELECT DISTINCT video_id 
        FROM transcriptions 
        WHERE propaganda = 1 
        LIMIT ?
    ''', (limit,))
    propaganda_1_videos = cursor.fetchall()

    # Get 100 videos with propaganda = 0
    cursor.execute('''
        SELECT DISTINCT video_id 
        FROM transcriptions 
        WHERE propaganda = 0 
        LIMIT ?
    ''', (limit,))
    propaganda_0_videos = cursor.fetchall()

    cursor.close()

    return [video_id[0] for video_id in propaganda_1_videos], [video_id[0] for video_id in propaganda_0_videos]

def main():
    setup_logging()
    access_token = load_token_from_file()

    try:
        db_path = 'C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/db/database.db'
        
        db_conn = get_db_connection(db_path)
        
        propaganda_1_videos, propaganda_0_videos = get_video_ids_from_db(db_conn, limit=100)

        for video_id in propaganda_1_videos:
            comments = fetch_video_comments(video_id, access_token)
            save_comments_to_db(db_conn, comments, 1)

        for video_id in propaganda_0_videos:
            comments = fetch_video_comments(video_id, access_token)
            save_comments_to_db(db_conn, comments, 0)

    except Exception as e:
        logging.critical(f"Failed to execute the main function with error: {e}")
    finally:
        if db_conn:
            db_conn.close()

if __name__ == "__main__":
    main()
