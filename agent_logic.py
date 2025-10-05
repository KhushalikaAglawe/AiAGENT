import pandas as pd
import sqlite3
import re
from googletrans import Translator 

# --- CONSTANTS ---
DB_FILE_NAME = 'feedback_data.db' 
TABLE_NAME = 'feedback_table'
FEEDBACK_COLUMN = 'Text'
SENTIMENT_COLUMN = 'Sentiment' 
# ✅ FIX: 'Confidence_SCORE' ko 'Confidence_Score' mein badla gaya.
CONFIDENCE_COLUMN = 'Confidence_Score' 

# --- INITIALIZE TRANSLATOR ---
translator = Translator()

# --- HELPER FUNCTIONS ---

def translate_text(text):
    """
    Translates text to English if the detected language is not English.
    Returns the original text if translation fails or if it's already English.
    """
    if not text or isinstance(text, (int, float)):
        return str(text) 
    
    text_str = str(text)
    
    try:
        detection = translator.detect(text_str)
        
        if detection.lang != 'en' and detection.confidence > 0.9:
            translated = translator.translate(text_str, dest='en')
            return translated.text
        
        return text_str 
        
    except Exception as e:
        return text_str


def categorize_feedback(text):
    """Categorizes feedback text into specific areas using English keywords."""
    text_lower = str(text).lower()
    
    if 'customer support' in text_lower or 'service was terrible' in text_lower or 'technical support' in text_lower or 'slow response' in text_lower:
        return 'Customer Support'
    elif 'product' in text_lower or 'quality' in text_lower or 'damaged' in text_lower or 'ordered' in text_lower or 'broken' in text_lower:
        return 'Product Quality'
    elif 'website' in text_lower or 'app' in text_lower or 'confusing' in text_lower or 'login' in text_lower or 'crashed' in text_lower:
        return 'Website/App'
    else:
        return 'General/Other'


def assign_priority(row):
    """Assigns a priority level based on sentiment and confidence score."""
    sentiment = row[SENTIMENT_COLUMN]
    confidence = row[CONFIDENCE_COLUMN]
    
    if sentiment == 'Negative' and confidence >= 0.75:
        return 'P1: Critical Issue 🚨'
    
    elif sentiment == 'Negative':
        return 'P2: High Priority'
    
    elif sentiment == 'Positive' and confidence >= 0.85:
        return 'P3: Top Positive 👍'
    
    else:
        return 'P4: Review Later'

# --- MAIN AGENT FUNCTION ---
def run_prioritization_agent():
    """Loads data, translates regional language, cleans, categorizes, and prioritizes feedback."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE_NAME)
        # 1. DATA LOAD
        df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
        
        if df.empty:
            return pd.DataFrame()
        
    except Exception as e:
        print(f"Error loading data from SQLite: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

    # 2. TRANSLATION STEP
    df['Translated_Text'] = df[FEEDBACK_COLUMN].apply(translate_text)


    # 3. DATA CLEANING & TYPE CONVERSION
    df[SENTIMENT_COLUMN] = df[SENTIMENT_COLUMN].fillna('Neutral').astype(str).str.strip() 
    # ✅ FIX: CONFIDENCE_COLUMN ab sahi hai
    df[CONFIDENCE_COLUMN] = pd.to_numeric(df[CONFIDENCE_COLUMN], errors='coerce').fillna(0.0)

    # 4. APPLY LOGIC (Now using 'Translated_Text' for categorization)
    df['Category'] = df['Translated_Text'].apply(categorize_feedback)
    df['Priority'] = df.apply(assign_priority, axis=1)

    # 5. SORTING & RENAMING
    priority_order = {
        'P1: Critical Issue 🚨': 1,
        'P2: High Priority': 2,
        'P3: Top Positive 👍': 3,
        'P4: Review Later': 4
    }
    df['Priority_Rank'] = df['Priority'].map(priority_order)
    
    df = df.rename(columns={'Text': 'Original_Text'})
    df = df.rename(columns={'Translated_Text': 'Text'}) 
    
    return df.sort_values(by=['Priority_Rank', CONFIDENCE_COLUMN], ascending=[True, False])