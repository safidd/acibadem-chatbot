import ollama
import psycopg2

def run_ai_pipeline():
    print("1. Pulling the embedding model via host network...")
    # This bypasses the Docker CLI network error by using the Python client
    ollama.pull('nomic-embed-text')
    print("Model pulled successfully!")

    print("2. Connecting to PostgreSQL...")
    try:
        # Connecting to the database via localhost port 5432
        conn = psycopg2.connect(
            dbname="acudb", user="acuuser", password="acupass", host="localhost", port="5432"
        )
        cursor = conn.cursor()

        print("3. Fetching scraped pages...")
        # Adjust 'webapp_page' to match your actual Django database table name if different
        cursor.execute("SELECT id, content FROM webapp_page WHERE embedding IS NULL;")
        pages = cursor.fetchall()

        if not pages:
            print("No new pages found to embed.")
            return

        for page_id, content in pages:
            print(f"Generating embedding for Page ID {page_id}...")
            response = ollama.embeddings(model='nomic-embed-text', prompt=content)
            
            # Update the page with the new 768-dimensional vector
            cursor.execute(
                "UPDATE webapp_page SET embedding = %s WHERE id = %s;",
                (response['embedding'], page_id)
            )

        conn.commit()
        print("4. Successfully stored all embeddings in pgvector!")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")
        print("Make sure your Django migrations have been applied so the table exists.")

if __name__ == "__main__":
    run_ai_pipeline()
