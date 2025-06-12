FROM apache/airflow:3.0.1

# Install all custom Python dependencies
RUN pip install --no-cache-dir \
    apache-airflow-providers-postgres \
    apache-airflow-providers-redis \
    nltk \
    transformers>=4.30.0 \
    torch>=2.0.0 \
    beautifulsoup4 \
    tqdm \
    psycopg2-binary \
    sentence-transformers
