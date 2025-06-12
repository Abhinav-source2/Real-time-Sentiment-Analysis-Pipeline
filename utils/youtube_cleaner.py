# utils/youtube_cleaner.py

import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_youtube_data():
    nltk.download('stopwords', quiet=True)

    input_path = os.path.join(os.getcwd(), 'data', 'youtube_comments_combined.csv')
    output_path = os.path.join(os.getcwd(), 'data', 'cleaned_youtube_comments.csv')
    comment_col = "Comment"

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    logger.info(f"Loading data from {input_path}")
    df = pd.read_csv(input_path)

    if comment_col not in df.columns:
        raise ValueError(f"Column '{comment_col}' not found in the data")

    stop_words = set(stopwords.words('english'))
    translator = str.maketrans('', '', string.punctuation)

    def clean_single_comment(comment):
        if pd.isna(comment):
            return ""
        text = str(comment).translate(translator).lower()
        return ' '.join(word for word in text.split() if word not in stop_words).strip()

    logger.info(f"Cleaning {len(df)} comments...")
    df['cleaned_comment'] = df[comment_col].apply(clean_single_comment)
    df = df[df['cleaned_comment'].str.len() > 0]

    df.to_csv(output_path, index=False)
    logger.info(f"Successfully cleaned {len(df)} comments. Output saved to {output_path}")

    return output_path
