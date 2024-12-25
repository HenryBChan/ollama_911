import json
from flask import Flask, request, jsonify
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
#from langchain.llms import LocalLLM
from langchain.llms import HuggingFacePipeline
from transformers import pipeline

# Initialize the Flask app
app = Flask(__name__)

# Load the TinyLLama model (assumes you have llama.cpp or equivalent configured)
#llm = LocalLLM(model_path="c:/Users/Lucas Chan/.ollama/models")
# Set up the Hugging Face pipeline for your local model
model_path = "c:/Users/Lucas Chan/.ollama/models"
generator = pipeline("text-generation", model=model_path)

# Wrap the pipeline in LangChain's LLM interface
llm = HuggingFacePipeline(pipeline=generator)

# Load the knowledge base (example: JSON file with emergency guidelines)
def load_knowledge_base():
    with open("../knowledge_base/emergency_guidelines.json", "r") as file:
        data = json.load(file)
    return data

knowledge_base = load_knowledge_base()

# Create a FAISS vector store for the knowledge base
embeddings = OpenAIEmbeddings()  # Replace with your embedding setup if needed
vector_store = FAISS.from_texts(
    texts=[item["procedure"] for item in knowledge_base],
    embedding=embeddings
)

# Set up RAG chain
qa_chain = RetrievalQA(
    retriever=vector_store.as_retriever(),
    llm=llm
)

# API endpoint for user query
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("query", "")
    if not user_input:
        return jsonify({"error": "No query provided"}), 400

    # Perform retrieval-augmented generation
    try:
        response = qa_chain.run(user_input)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main endpoint to test server status
@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "911 Help Assistant is running."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
