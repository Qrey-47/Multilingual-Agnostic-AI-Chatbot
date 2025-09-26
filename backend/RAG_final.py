import os
import numpy as np
from pymongo import MongoClient
from numpy.linalg import norm

# LangChain imports
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import CTransformers  # Local LLaMA via ctransformers

# ------------------------
# 1️⃣ Setup MongoDB
# ------------------------
MONGO_URI = os.getenv("MONGO_URI")
assert MONGO_URI, "Set the MONGO_URI environment variable in your .env file"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
assert GOOGLE_API_KEY, "Set the GOOGLE_API_KEY environment variable in your .env file"

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["edumate"]
collection = db["notices"]

# ------------------------
# 2️⃣ Embedding model: all-MiniLM-L6-V2
# ------------------------
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text: str) -> np.ndarray:
    """Get embedding for text using HuggingFace MiniLM model"""
    emb = embedding_model.embed_query(text)
    return np.array(emb, dtype=np.float32)

# ------------------------
# 3️⃣ LLM: Local LLaMA (TheBloke/Llama-2-7B-GGML)
# ------------------------
llm = CTransformers(
    model="TheBloke/Llama-2-7B-GGML",  # path or HF repo
    model_type="llama",
    config={'max_new_tokens': 256, 'temperature': 0.2}
)

# ------------------------
# 4️⃣ Insert new notice with embedding
# ------------------------
def add_notice(title, content, category="General", author="Admin", tags=None):
    if tags is None:
        tags = []
    full_text = f"{title} {content}"
    embedding = get_embedding(full_text).tolist()  # list for MongoDB
    doc = {
        "title": title,
        "content": content,
        "category": category,
        "author": author,
        "tags": tags,
        "embedding": embedding
    }
    collection.insert_one(doc)
    print("✅ Notice inserted successfully.")

# ------------------------
# 5️⃣ Search for relevant notices by cosine similarity
# ------------------------
def search_notices(query, top_k=3):
    """Search for relevant notices using cosine similarity on stored embeddings"""
    query_embedding = get_embedding(query)
    docs = list(collection.find({"embedding": {"$exists": True}}))

    scored_docs = []
    for d in docs:
        emb = np.array(d["embedding"], dtype=np.float32)
        if emb.size == 0:
            continue
        sim = np.dot(query_embedding, emb) / (norm(query_embedding) * norm(emb))
        scored_docs.append((sim, d))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return scored_docs[:top_k]

# ------------------------
# 6️⃣ Build prompt for LLaMA LLM
# ------------------------
def build_prompt(query, top_docs):
    context = "\n\n".join([f"Title: {d['title']}\nContent: {d['content']}" for _, d in top_docs])
    prompt = f"""You are a helpful assistant that answers questions using the notices database.

Context:
{context}

Question: {query}

Answer:"""
    return prompt

# ------------------------
# 7️⃣ Answer a query
# ------------------------
def answer_query(query, top_k=3):
    top_docs = search_notices(query, top_k)
    if not top_docs:
        return "No relevant notices found."
    prompt = build_prompt(query, top_docs)
    answer = llm(prompt)
    return answer

# ------------------------
# 8️⃣ Example usage
# ------------------------
if __name__ == "__main__":
    # Insert a new notice
    add_notice(
        title="Semester Exam Schedule Released",
        content="The semester exams for 2025 will be held from 1st Dec to 15th Dec.",
        category="Examination",
        tags=["exam", "schedule", "semester"]
    )

    # Ask a question
    answer = answer_query("When are the semester exams?")
    print("Answer:", answer)

