import os
import numpy as np
from pymongo import MongoClient
from numpy.linalg import norm

# Imports for LangChain + Gemini
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# ------------------------
# 1️⃣ Setup MongoDB
# ------------------------
MONGO_URI = "mongodb+srv://adityaS:ADIScollege@collegecluster.iauhe6t.mongodb.net/?retryWrites=true&w=majority&appName=CollegeCluster"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["edumate"]
collection = db["notices"]

# Make sure your Google API key is set
# e.g. export GOOGLE_API_KEY="your_key"
assert "GOOGLE_API_KEY" in os.environ, "Set the GOOGLE_API_KEY environment variable"

# ------------------------
# 2️⃣ Embedding model: Gemini embeddings
# ------------------------
embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

def get_embedding(text: str) -> np.ndarray:
    """Get embedding for text using Gemini embedding API"""
    emb = embedding_model.embed_query(text)
    return np.array(emb, dtype=np.float32)

# ------------------------
# 🔄 Update all existing embeddings to Gemini
# ------------------------
for doc in collection.find({}):
    full_text = f"{doc['title']} {doc['content']}"
    emb = get_embedding(full_text).tolist()  # Gemini embedding, 3072-dim
    collection.update_one({"_id": doc["_id"]}, {"$set": {"embedding": emb}})

print("✅ All existing embeddings updated to Gemini.")


# ------------------------
# 3️⃣ LLM: Gemini chat model
# ------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # or your preferred Gemini variant
    temperature=0.2,
    max_tokens=256
)

# ------------------------
# 4️⃣ Insert new notice with embedding
# ------------------------
def add_notice(title, content, category="General", author="Admin", tags=None):
    if tags is None:
        tags = []
    full_text = f"{title} {content}"
    embedding = get_embedding(full_text).tolist()
    doc = {
        "title": title,
        "content": content,
        "category": category,
        "author": author,
        "tags": tags,
        "embedding": embedding
    }
    collection.insert_one(doc)
    print("✅ Notice inserted successfully with Gemini embedding.")

# ------------------------
# 5️⃣ Search for relevant notices by cosine similarity
# ------------------------
def search_notices(query, top_k=3):
    query_embedding = get_embedding(query)
    docs = list(collection.find({"embedding": {"$exists": True}}))
    scored = []
    for d in docs:
        emb = np.array(d["embedding"], dtype=np.float32)
        if emb.size == 0:
            continue
        sim = float(np.dot(query_embedding, emb) / (norm(query_embedding) * norm(emb)))
        scored.append((sim, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]

# ------------------------
# 6️⃣ Build prompt for Gemini
# ------------------------
def build_prompt(query, top_docs):
    context = "\n\n".join([f"Title: {d['title']}\nContent: {d['content']}" for _, d in top_docs])
    prompt = f"""You are an assistant that answers student questions using the college notices database.

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
    # Gemini’s chat model expects a list of messages format
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    resp = llm.invoke(messages)  # returns a response object
    return resp.content  # or .content depending on version

# ------------------------
# 8️⃣ Example usage
# ------------------------
if __name__ == "__main__":
    add_notice(
        title="Semester Exam Schedule Released",
        content="The semester exams for 2025 will be held from 1st Dec to 15th Dec.",
        category="Examination",
        tags=["exam", "schedule", "semester"]
    )

    ans = answer_query("When are the semester exams?")
    print("Answer:", ans)
