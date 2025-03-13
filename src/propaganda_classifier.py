import sqlite3
import logging
from transformers import pipeline

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

hypothesis_template = "This text is {}"
classes_verbalized = ["russian propaganda", "not russian propaganda", "unclear"]
zeroshot_classifier = pipeline("zero-shot-classification", model="MoritzLaurer/deberta-v3-large-zeroshot-v2.0")

conn = sqlite3.connect('C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/db/database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT id, description FROM data WHERE processed = 0")
batch_size = 2000 

try:
    while True:
        descriptions = cursor.fetchmany(batch_size)
        logging.info("Fetching videos")
        if not descriptions:
            break
        for description in descriptions:
            text = description['description']
            row_id = description['id']
            logging.info("Proccessing video")
            output = zeroshot_classifier(text, classes_verbalized, hypothesis_template=hypothesis_template, multi_label=False)
            label = output['labels'][0]
            confidence = output['scores'][0]

            if label == 'russian propaganda' and confidence > 0.6:
                cursor.execute("UPDATE data SET propaganda = 1, processed = 1 WHERE id = ?", (row_id,))
            elif label == 'not russian propaganda' and confidence > 0.6:
                cursor.execute("UPDATE data SET propaganda = 0, processed = 1 WHERE id = ?", (row_id,))
            else:
                cursor.execute("UPDATE data SET unclear = 1, processed = 1 WHERE id = ?", (row_id,))
            conn.commit()
finally:
    conn.close()
