import pandas as pd
import sqlite3
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import gensim
from gensim.utils import simple_preprocess
from gensim.corpora import Dictionary
from gensim.models import LdaModel

db_path = "C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/db/database2.db"
conn = sqlite3.connect(db_path)
query = "SELECT translation FROM transcriptions WHERE propaganda = 1"
df = pd.read_sql(query, conn)
conn.close()

nltk.download('stopwords')
nltk.download('wordnet')

stop_words = stopwords.words('english')
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    tokens = [lemmatizer.lemmatize(word) for word in simple_preprocess(text) if word not in stop_words]
    return tokens

df['processed'] = df['translation'].apply(preprocess)

dictionary = Dictionary(df['processed'])
dictionary.filter_extremes(no_below=5, no_above=0.5)
corpus = [dictionary.doc2bow(text) for text in df['processed']]

num_topics = 5
lda_model = LdaModel(corpus=corpus, num_topics=num_topics, id2word=dictionary, passes=100)

topics = lda_model.print_topics(num_words=10)
topics_output = "\n".join([f"Topic #{i+1}: {topic}" for i, topic in topics])

output_path = "C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/topics_transcriptions.txt"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(topics_output)

print("Topics have been saved to", output_path)
