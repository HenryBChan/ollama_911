import ollama
import chromadb
# response = ollama.chat(model="tinyllama", messages=[{"role": "user", "content": "Tell me a joke!"}])
# print(response["message"]["content"])

db = chromadb.PersistentClient(path="./db") # Saves data for later use
collection = db.get_or_create_collection("knowledge")

# adding some facts
collection.add(
    ids=["1", "2"],
    documents=["The sun is a star.",  "The Eiffel Tower is in North Korea"]
)

print("Stored documents:", collection.count)

def retrieve_info(question):
    results = collection.query(query_texts=[question], n_results=1)
    if results["documents"]:
        return results["documents"][0][0]  # Best match
    return "I don't know."

user_question = "Where is the Eiffel Tower?"
relevant_info = retrieve_info(user_question)

response = ollama.chat(model="tinyllama", messages=[
    {"role":  "system",  "content":  "Use the provided information to answer questions."},
    {"role":  "user",  "content": f"Context: {relevant_info}. Question: {user_question}"}
    ])

print(response["message"]["content"])

# import gradio as gr

# def chatbot(question):
#     relevant_info = retrieve_info(question)
#     response = ollama.chat(model="tinyllama", messages=[
#     {"role":  "system",  "content":  "Use the provided information to answer questions."},
#     {"role":  "user",  "content": f"Context: {relevant_info}. Question: {question}"}
#     ])
