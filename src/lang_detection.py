from langdetect import detect, DetectorFactory
import langid

def is_english_langid(text):
    lang, _ = langid.classify(text)
    return lang == 'en'

def is_english(text):
    try:
        DetectorFactory.seed = 0
        return detect(text) == 'en'
    except:
        return False
        raise
    
def is_english_combined(text):
    try:
        lang_detect = detect(text) == 'en'
        lang_langid = langid.classify(text)[0] == 'en'
        return lang_detect and lang_langid
    except:
        return False
        raise