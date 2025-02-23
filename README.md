# ollama_911
Using local LLM model in RAG setup to service 911 requests.

Creating a Python application for assisting users in prompting text for 911 help using a Retrieve-Augmented Generation (RAG) setup and a downloaded TinyLLama model involves several components. Below is an example plan and Python code to get started.
-------------------------------
Plan for the 911 Help Application
1. Purpose:
   * Provide guided responses to emergency queries.
   * Ensure proper categorization and prioritization of requests.
2. Key Features:
   * Text Input: User submits a free-form text request (e.g., "My house is on fire").
   * Triage: Use RAG to classify and provide procedural responses (e.g., "Call the fire department immediately").
   * Knowledge Base: Include structured knowledge (e.g., emergency procedures, FAQs) to enhance responses.
3. Components:
   * Pre-trained TinyLLama Model: For generating responses.
   * Knowledge Base: A collection of emergency guidelines (stored as JSON or a database).
   * RAG Workflow:
      1. Query the knowledge base for relevant information.
      2. Use the TinyLLama model to generate context-aware responses.
   * Python Frameworks:
      * Use langchain for RAG orchestration.
      * Use Flask or FastAPI to create a web-based or local application interface.


SETUP
   pip install flask langchain faiss-cpu 
   pip install -U langchain-community
   pip install transformers
   pip install tensorflow

Run the Application:
   Using tinyllama directly use : ollama run tinyllama
   Start the Flask server:
   python bin/main.py

Send Requests:
   Use a tool like postman or curl to test:
   curl -X POST http://127.0.0.1:5000/ask \
     -H "Content-Type: application/json" \
     -d '{"query": "My house is on fire"}'

Next Steps
   * Enhance the Knowledge Base: Add detailed guidelines for various emergencies.
   * Integrate NLP Pipelines: Include advanced preprocessing for better user input handling.
   * Deploy: Use Docker or cloud platforms (e.g., AWS, Azure) for production use.
Would you like help refining this plan, customizing the RAG pipeline, or expanding the emergency procedures?



TODO: 
   * fix the tts 
   * build a pygame frontend user interface.  We want to have button that is enabled when user can click to speak.  The button is a phone handset image.  When user depresses the button and holds the button down, the microphone is recording.  When user releases the button the recording stops.  When user is speaking on the pygame frontend we have a little spectrum visualization of the user speaking.  On the reverse side when the backend places a recording back from a tts engine, there is a seperate spectrum to visualize the speach being sent back to the user.  