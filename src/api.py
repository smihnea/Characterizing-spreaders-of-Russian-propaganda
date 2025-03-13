import requests
import logging

def make_api_request(url, headers, query_body, query_params):
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=query_body, params=query_params)
            logging.info(f"[API]: API request made with status code {response.status_code}")
            if response.status_code == 200:
                json_response = response.json()
                return json_response
            else:
                logging.critical(f"[API]: Attempt {attempt + 1} failed with status code {response.status_code}")
                logging.critical(f"[API]: Error details: {response.text}")
        except requests.RequestException as e:
            logging.critical(f"[API]: Request failed with exception {e}")
    return None
