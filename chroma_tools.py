import chromadb

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="school_data"
)

def get_student_records(name):

    results = collection.query(
        query_texts=[name],
        n_results=20
    )

    filtered_docs = []

    for doc in results["documents"][0]:

        if name.lower() in doc.lower():

            filtered_docs.append(doc)

    return filtered_docs
