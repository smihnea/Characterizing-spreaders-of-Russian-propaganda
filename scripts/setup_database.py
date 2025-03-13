import sqlite3

def setup_database():
    try:
        conn = sqlite3.connect('C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/db/database2.db')
        c = conn.cursor()

# Create video_extract table with mutiple columns
        c.execute('''
        CREATE TABLE IF NOT EXISTS video_extract (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            username TEXT,
            description TEXT,
            region_code TEXT,
            hashtags TEXT,
            view_count INTEGER,
            likes INTEGER,
            comment_count INTEGER,
            create_time INTEGER,
            downloaded BOOLEAN DEFAULT 0,
            transcribed BOOLEAN DEFAULT 0,
            propaganda BOOLEAN DEFAULT 0,
            not_russian_propaganda BOOLEAN DEFAULT 0,
            unclear BOOLEAN DEFAULT 0
        )
        ''')
               
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print("Error occurred:", e)

# Combine 2 tables
# def combine_tables():
#     try:
#         conn = sqlite3.connect('C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/db/database2.db')
#         c = conn.cursor()

#         # Insert entries from video_data to video_extract
#         c.execute('''
#         INSERT INTO video_extract (video_id, username, description, region_code, hashtags, view_count, likes, comment_count, create_time, downloaded, transcribed, propaganda)
#         SELECT video_id, username, description, region_code, hashtags, view_count, likes, comment_count, create_time, downloaded, transcribed, propaganda
#         FROM video_data
#         ''')

#         conn.commit()
#         conn.close()
#         print("Data combined successfully.")
#     except sqlite3.Error as e:
#         print("Error occurred:", e)


# Delete a table
# def delete_video_data_table():
#     try:
#         conn = sqlite3.connect('C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/db/database2.db')
#         c = conn.cursor()

#         # Drop the video_data table
#         c.execute('DROP TABLE IF EXISTS video_data')

#         conn.commit()
#         conn.close()
#         print("video_data table deleted successfully.")
#     except sqlite3.Error as e:
#         print("Error occurred:", e)

if __name__ == "__main__":
    setup_database()
