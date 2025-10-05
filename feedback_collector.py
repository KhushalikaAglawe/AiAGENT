import pandas as pd
import sqlite3
from datetime import datetime
import random

DB_FILE = 'feedback_data.db' 
TABLE_NAME = 'feedback_table'

def add_new_feedback(feedback_list):
    """Inserts a list of new feedback items into the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        
        # Agar table exist nahi karti to banao
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                "Date/Time" TEXT,
                Text TEXT,
                Sentiment TEXT,
                Confidence_Score REAL,
                User_ID INTEGER
            )
        """)
        
        # Convert the list of feedback into a DataFrame
        df_new = pd.DataFrame(feedback_list)
        
        # Date/Time ko ISO format mein store karo (sqlite standard)
        df_new['Date/Time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Append data to the existing table
        df_new.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
        print(f"✅ Successfully inserted {len(feedback_list)} new feedback item(s) into {DB_FILE}.")

    except Exception as e:
        print(f"❌ Error inserting data: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    
    # --- Sample Feedback Texts for Variety (English) ---
    sample_texts = [
        'Login page is crashing every time I try to access. This is a critical issue!',
        'The app is unusable after the last update. I lost all my settings.',
        'Customer support took 5 days to reply, terrible and unacceptable service.',
        'My order arrived damaged. Product quality is very poor.',
        'Payment gateway failed multiple times, leading to a lost sale.',
        'Website navigation is confusing and slow. Fix it ASAP.',
        'The new search feature gives irrelevant results.',
        'Refund process is too complicated and takes weeks.',
        'I received the wrong item, quite disappointed with the shipping.',
        'The mobile view of the dashboard looks broken.',
        'I love the new product updates, very satisfied! Best purchase ever.',
        'The user interface is fantastic! So intuitive and fast.',
        'Customer support resolved my issue in minutes. Excellent service!',
        'This is exactly what I was looking for. Top quality!',
        'The checkout process was super smooth and fast. Great job!',
        'Everything was fine, average experience.',
        'The colors are nice, but the size is slightly off.',
        'Just needed a quick check, data loaded correctly.',
        'I wish there were more filtering options in the sidebar.',
        'No major issues, but the font size could be larger.'
    ]
    
    new_data = []
    
    # --- GENERATE 50 ENGLISH DATA ENTRIES ---
    for i in range(50):
        text = random.choice(sample_texts)
        
        # Smart Sentiment Assignment (Simulating AI for Priority)
        if 'crash' in text or 'terrible' in text or 'broken' in text or 'poor quality' in text:
            sentiment = 'Negative'
            confidence = random.uniform(0.70, 0.99)
        elif 'love' in text or 'satisfied' in text or 'excellent' in text or 'fantastic' in text:
            sentiment = 'Positive'
            confidence = random.uniform(0.85, 0.99)
        else:
            sentiment = random.choice(['Neutral', 'Negative', 'Positive'])
            confidence = random.uniform(0.40, 0.85)
            
        
        entry = {
            'Text': text,
            'Sentiment': sentiment,
            'Confidence_Score': confidence,
            'User_ID': 1001 + random.randint(1, 100)
        }
        new_data.append(entry)
    
    # --- ADD 5 REGIONAL LANGUAGE (HINDI) TEST ENTRIES ---
    new_data.extend([
        {
            # Entry 1: Critical Issue in Hindi (P1 expected) - Website/App issue
            'Text': 'वेबसाइट क्रैश हो रही है और भुगतान नहीं हो पा रहा है। यह एक गंभीर समस्या है!', 
            'Sentiment': 'Negative', 
            'Confidence_Score': random.uniform(0.90, 0.99), 
            'User_ID': 8001
        },
        {
            # Entry 2: High Priority Negative (P2 expected) - Customer Support/Delivery issue
            'Text': 'मैंने जो उत्पाद ऑर्डर किया था वह बहुत देर से आया और ग्राहक सहायता ने जवाब नहीं दिया।', 
            'Sentiment': 'Negative',
            'Confidence_Score': random.uniform(0.70, 0.80),
            'User_ID': 8002
        },
        {
            # Entry 3: Top Positive (P3 expected) - Product Quality
            'Text': 'उत्पाद बहुत अच्छा है, मुझे यह वास्तव में पसंद आया। मैं बहुत संतुष्ट हूँ!', 
            'Sentiment': 'Positive',
            'Confidence_Score': random.uniform(0.95, 0.99),
            'User_ID': 8003
        },
        {
            # Entry 4: Neutral/Review Later (P4 expected) - General/Other
            'Text': 'डिलीवरी का समय ठीक था, लेकिन पैकेजिंग थोड़ी खराब थी।', 
            'Sentiment': 'Neutral',
            'Confidence_Score': random.uniform(0.50, 0.65),
            'User_ID': 8004
        },
        {
            # Entry 5: Negative about Product Quality (P2 expected)
            'Text': 'उत्पाद की गुणवत्ता बहुत खराब है और यह कुछ ही दिनों में टूट गया।', 
            'Sentiment': 'Negative',
            'Confidence_Score': random.uniform(0.75, 0.85),
            'User_ID': 8005
        }
    ])

    # Insert all data into the database
    add_new_feedback(new_data)
    print("\n--- To check the dashboard, run: streamlit run app.py ---")