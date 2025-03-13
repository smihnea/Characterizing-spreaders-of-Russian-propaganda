import sqlite3
import logging

def get_db_connection(database_path):
    try:
        conn = sqlite3.connect(database_path)
        return conn
    except sqlite3.Error as e:
        logging.critical(f"Failed to connect to database with error: {e}")
        raise e

def save_video_data_to_db(conn, video_id, username, description, region_code, hashtag_names, view_count, likes, comment_count, create_time):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT video_id FROM data WHERE video_id = ?", (video_id,))
        existing = cursor.fetchone()
        if existing:
            logging.info(f"[DB]: {video_id} already exists in the database.")
        else:
            logging.info("[DB]: New candidate found! Saving to database")
            hashtag_string = ','.join(hashtag_names)
            cursor.execute("""
                INSERT INTO data (video_id, username, description, region_code, hashtags, view_count, likes, comment_count, create_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (video_id, username, description, region_code, hashtag_string, view_count, likes, comment_count, create_time))
            conn.commit()
            logging.info(f"[DB]: Successfully saved video with video_id: {video_id} to the database.")
    except sqlite3.Error as e:
        logging.error(f"[DB]: SQLite error: {e}")
    finally:
        cursor.close()




