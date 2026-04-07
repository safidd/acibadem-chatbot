import ollama
import psycopg2
import json

def test_semantic_search(query):
    print(f"1. Generating embedding for the query: '{query}'...")
    query_embedding = ollama.embeddings(model='nomic-embed-text', prompt=query)['embedding']
    
    print("2. Connecting to PostgreSQL to perform vector search...")
    try:
        conn = psycopg2.connect(
            dbname="acudb", user="acuuser", password="acupass", host="localhost", port="5432"
        )
        cursor = conn.cursor()
        
        # pgvector uses the <=> operator to calculate cosine distance between vectors
        # A lower distance means the text is more semantically similar to the question
        cursor.execute("""
            SELECT id, content, embedding <=> %s::vector AS distance
            FROM webapp_page
            WHERE embedding IS NOT NULL
            ORDER BY distance ASC
            LIMIT 3;
        """, (json.dumps(query_embedding),))
        
        results = cursor.fetchall()
        
        print("\n--- Top 3 Semantic Search Results ---")
        if not results:
            print("No results found. The database might be empty.")
        else:
            for row in results:
                page_id = row[0]
                content = row[1]
                distance = row[2]
                print(f"Page ID: {page_id} | Similarity Distance: {distance:.4f}")
                print(f"Snippet: {content[:200].strip()}...\n")
                
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    # You can change this question to test different edge cases
    test_question = "What are the engineering programs and computer science courses?"
    test_semantic_search(test_question)
