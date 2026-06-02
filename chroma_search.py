import chromadb

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    "students"
)

results = collection.query(
    query_texts=[
        "Which student has attendance 92 percent?"
    ],
    n_results=3
)

for doc in results["documents"][0]:

    print(doc)

    print("=" * 50)