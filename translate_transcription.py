import sqlite3
from transformers import pipeline

translation_pipeline = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en")

def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    return conn

def fetch_transcriptions(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, transcription 
        FROM transcriptions 
        WHERE translation IS NULL OR translation = ''
    ''')
    return cursor.fetchall()

def update_translation(conn, translation_data):
    cursor = conn.cursor()
    for trans_id, translation in translation_data:
        cursor.execute('''
            UPDATE transcriptions 
            SET translation = ? 
            WHERE id = ?
        ''', (translation, trans_id))
    conn.commit()
    cursor.close()

def main():
    db_path = 'C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/db/database.db'

    conn = get_db_connection(db_path)

    try:
        transcriptions = fetch_transcriptions(conn)

        translation_data = []
        for trans_id, transcription_text in transcriptions:
            translated_text = translation_pipeline(transcription_text)[0]['translation_text']
            translation_data.append((trans_id, translated_text))

        update_translation(conn, translation_data)
        print("Translation completed and database updated successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
