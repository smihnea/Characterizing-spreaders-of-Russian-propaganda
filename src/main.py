import argparse
import datetime
import json
import logging
import requests

from lang_detection import is_english_combined
from db import save_video_data_to_db, get_db_connection
from api import make_api_request

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,  
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def load_token_from_file():
    with open('C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/token_config.json', 'r') as f:
        token_data = json.load(f)
    return token_data['access_token']

def video_exists(conn, video_id):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM data WHERE video_id = ?", (video_id,))
    exists = cursor.fetchone() is not None
    cursor.close()
    return exists

def process_video_data(videos_data, conn):
    if not videos_data:
        logging.warning( "No videos data found.")
        return

    video_list = videos_data.get("data", {}).get("videos", [])
    if not video_list:
        logging.warning("No videos found.")
        return

    for video in video_list:
        video_id = video.get("id")
        username = video.get("username")
        video_description = video.get("video_description")
        region_code = video.get("region_code")
        hashtag_names = video.get("hashtag_names", [])
        like_count = video.get("like_count")
        comment_count = video.get("comment_count")
        view_count = video.get("view_count")
        create_time = video.get("create_time")

        if is_english_combined(video_description):
            save_video_data_to_db(conn, video_id, username, video_description, region_code, hashtag_names, view_count, like_count, comment_count, create_time)
    else:
            logging.info(f"Video with video_id: {video_id} already exists in the database.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run video data processing for specific weeks and executions.")
    parser.add_argument("--weeks_to_run", type=int, default=4, help="Number of weeks to run the program.")
    return parser.parse_args()
    

def main():
    args = parse_arguments()
    setup_logging()
    url = "https://open.tiktokapis.com/v2/research/video/query"
    initial_start_date = datetime.datetime(2023, 1, 3)
    access_token = load_token_from_file()
    hashtags = ["istandwithputin", "istandwithrussia", "iloverussia", "prayforrussia", "donetsk", "donbas", "russia", "putin","vladimirputin", "wagner", "prayforrussia", "bakhmut", "slavarussia", "naziukraine", "ukrainecorrupt"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    query_params = {
        "fields": "id,username,video_description,region_code,hashtag_names,like_count,comment_count,view_count,create_time"
    }
    cursor = 0
    try:
        db_conn = get_db_connection('C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/db/database.db')
        try:
            for week in range(args.weeks_to_run):
                start_date = initial_start_date + datetime.timedelta(weeks=week)
                end_date = start_date + datetime.timedelta(days=6)
                start_date_str = start_date.strftime('%Y%m%d')
                end_date_str = end_date.strftime('%Y%m%d')


                logging.info(f"[DATE]: Searching for candidates from {start_date_str} to {end_date_str}. Processing week {week+1}")
                
                cursor = 0
                has_more = True
                search_id = ""
               
                while has_more:
                    query_body = {
                        "query": {
                            "or": [
                                {
                                    "operation": "IN",
                                    "field_name": "hashtag_name",
                                    "field_values": hashtags
                                },
                                {
                                    "operation": "IN",
                                    "field_name": "keyword",
                                    "field_values": hashtags
                                }
                            ]
                        },
                        "start_date": start_date_str,
                        "end_date": end_date_str,
                        "max_count": 100,
                        "search_id": search_id,
                        "cursor": cursor,
                    }
                    response = make_api_request(url, headers, query_body, query_params)
                    if response and 'data' in response and 'videos' in response['data']:
                        process_video_data(response, db_conn)
                        cursor = response['data'].get('cursor', 0)
                        search_id = response['data'].get('search_id', "")
                        has_more = response['data'].get('has_more', False)
                        logging.info("Continuing to next batch.")
                    else:
                        has_more = False
                        logging.error(f"No more data or API Request failed")

                logging.info(f"Completed processing for week {week+1}. No more videos to fetch from {start_date_str} to {end_date_str}.")
                
        except Exception as e:
            logging.critical(f"Failed to execute the main function with error: {e}")
        finally:
            db_conn.close()
    except Exception as e:
        logging.critical(f"Failed to execute the main function with error: {e}")

if __name__ == "__main__":
    main()

