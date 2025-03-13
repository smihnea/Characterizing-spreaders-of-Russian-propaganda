import sqlite3
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import spacy
import re

nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s\U00010000-\U0010FFFF]', '', text)
    text = text.strip()
    return text

db_path = 'C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/db/database.db'
print(f"Attempting to connect to database at: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Database connected.")

absa_model_name = "yangheng/deberta-v3-base-absa-v1.1"
absa_tokenizer = AutoTokenizer.from_pretrained(absa_model_name)
absa_model = AutoModelForSequenceClassification.from_pretrained(absa_model_name)

absa_pipeline = pipeline("sentiment-analysis", model=absa_model, tokenizer=absa_tokenizer)

cursor.execute("SELECT id, description FROM transcriptions")
rows = cursor.fetchall()

print(f"Number of rows in database: {len(rows)}")

aspects = ["Russia", "Ukraine", "Putin", "Zelensky", "Nato"]

for row in rows:
    row_id, description = row
    combined_text = description
    combined_text = preprocess_text(combined_text)
    doc = nlp(combined_text)

    mentioned_aspects = []
    for ent in doc.ents:
        if ent.label_ in ["GPE", "ORG", "PERSON"]:
            for aspect in aspects:
                if aspect.lower() == ent.text.lower():
                    mentioned_aspects.append(aspect)
    
    if not mentioned_aspects:
        for aspect in aspects:
            if aspect.lower() in combined_text.lower():
                mentioned_aspects.append(aspect)

    mentioned_aspects = list(set(mentioned_aspects))

    aspects_results = []
    sentiments_results = []

    if mentioned_aspects:
        for aspect in mentioned_aspects:
            result = absa_pipeline(f"What is the sentiment towards {aspect} in: {combined_text}")

            aspect_result = str(aspect)
            sentiment_result = str(result[0]['label'])
            
            print(f"Aspect: {aspect_result}, Sentiment: {sentiment_result}")
            
            aspects_results.append(aspect_result)
            sentiments_results.append(sentiment_result)
    else:
        aspects_results.append("None")
        sentiments_results.append("None")

    aspects_str = ', '.join(aspects_results)
    sentiments_str = ', '.join(sentiments_results)
    
    try:
        cursor.execute("""
            UPDATE transcriptions 
            SET aspect = ?, sentiment = ?
            WHERE id = ?
        """, (aspects_str, sentiments_str, row_id))
        print(f"Row {row_id} updated successfully.")

        conn.commit()

        cursor.execute("SELECT aspect, sentiment FROM transcriptions WHERE id = ?", (row_id,))
        updated_row = cursor.fetchone()
        
    except sqlite3.Error as e:
        print(f"An error occurred while updating row {row_id}: {e}")
        conn.rollback()

conn.close()