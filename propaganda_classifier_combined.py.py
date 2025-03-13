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

setup_logging()

hypothesis_template = "This text is {} regarding the Russian invasion of Ukraine."
classes_verbalized = [
    "pro russia",
    "anti russia",
    "unclear",
]
zeroshot_classifier = pipeline("zero-shot-classification", model="MoritzLaurer/deberta-v3-large-zeroshot-v2.0")

conn = sqlite3.connect('C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/db/database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT rowid, description, translation FROM transcriptions WHERE translation IS NOT NULL AND translation != ''")
batch_size = 2000

try:
    while True:
        descriptions = cursor.fetchmany(batch_size)
        if not descriptions:
            break 
        for description in descriptions:
            combined_text = f"{description['description']} {description['translated_text']}"
            row_id = description['rowid']
            logging.info(f"Processing row ID: {row_id}")
            output = zeroshot_classifier(combined_text, classes_verbalized, hypothesis_template=hypothesis_template, multi_label=False)
            label = output['labels'][0]
            confidence = output['scores'][0]

            if label == 'pro russia' and confidence > 0.6:
                cursor.execute("UPDATE transcriptions SET propaganda = 1, unclear = 0 WHERE rowid = ?", (row_id,))
            elif label == 'anti russia' and confidence > 0.6:
                cursor.execute("UPDATE transcriptions SET propaganda = 0, unclear = 0 WHERE rowid = ?", (row_id,))
            else:
                cursor.execute("UPDATE transcriptions SET unclear = 1 WHERE rowid = ?", (row_id,))
            conn.commit()
finally:
    conn.close()
