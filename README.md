A smart agricultural assistant built with Python, FastAPI, Streamlit, LangChain, FAISS, and OpenAI. The app allows users to upload agricultural documents (PDF/TXT), index them into a local vector store, and ask questions about crops, soil, irrigation, pests, fertilizers, and government schemes in English or Tamil.

## Overview

This project is designed as a document-grounded AI assistant for agriculture-related queries. It combines:

- a FastAPI backend for document ingestion and question answering
- a Streamlit frontend for an interactive chat interface
- FAISS vector search for retrieving relevant context
- OpenAI embeddings and language models for intelligent responses

The system answers only agriculture-related questions and rejects unrelated queries.

---

## Features

- Upload multiple PDF or TXT files
- Automatically process uploaded documents
- Split large documents into chunks for efficient indexing
- Store document embeddings in a FAISS vector database
- Retrieve the most relevant document context for each question
- Ask questions through a chat interface
- Support English and Tamil responses
- Restrict answers to agriculture-related topics only

---

## Tech Stack

- Python
- FastAPI
- Streamlit
- LangChain
- FAISS
- OpenAI API
- PyMuPDF / PyPDF
- Playwright (for web ingestion workflow)

---

## Project Structure

```text
Agricultural_bot/
├── backend.py                # FastAPI backend for upload and chat generation
├── frontend.py               # Streamlit UI for the assistant
├── playwright ingestion.py   # Optional web ingestion script
├── Documents/               # Uploaded local files
├── faiss_index/             # Local FAISS vector store
├── .env                     # Environment variables (not committed)
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
├── tn_uzhavan_goschemes.json # Optional scheme metadata
└── .gitignore
```

---

## Prerequisites

Before running the project, make sure you have:

- Python 3.9+
- An OpenAI API key
- A local environment capable of installing Python packages
- Playwright browser support if you plan to use the ingestion script

---

## Installation

1. Open a terminal in the project folder:

```bash
cd Builathon_Projects/Agricultural_bot
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install the Playwright browser dependency:

```bash
playwright install chromium
```

5. Create a `.env` file in the project root with your OpenAI key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Optional LangSmith tracing settings:

```env
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=<project anme>
```

---

## Run the Application

### Start the backend

```bash
uvicorn backend:app --reload --host 0.0.0.0 --port 8000
```

### Start the frontend

In a separate terminal:

```bash
streamlit run frontend.py
```

Then open the local Streamlit URL shown in the terminal, usually:

```text
http://localhost:8501
```

---

## How It Works

1. The user uploads one or more PDF/TXT documents in the Streamlit app.
2. The FastAPI backend saves the files in the `Documents/` folder.
3. The uploaded content is split into chunks and converted to vector embeddings.
4. The embeddings are stored in a FAISS index (`faiss_index/`).
5. When a question is asked, the app retrieves the most relevant chunks from the vector store.
6. The retrieved context is sent to GPT along with the prompt.
7. The model answers using the uploaded agricultural context, in the selected language.

---

## Example Queries

- What is the best irrigation method for cotton cultivation?
- How can I control pest attacks in tomato crops?
- Explain the eligibility for a government agriculture scheme.
- What are the recommended fertilizers for rice fields?

---

## Notes

- The project is built for agricultural document Q&A and is intentionally restricted to relevant agricultural topics.
- If the question is unrelated to agriculture or farming, it responds with a refusal message.
- The vector index persists in the local `faiss_index/` folder and can be reused across sessions.

---

## Troubleshooting

If the app is not working:

- Check that the backend is running on port 8000
- Verify your `OPENAI_API_KEY` is present in `.env`
- Make sure the uploaded file is a valid PDF or TXT
- Confirm that all dependencies are installed from `requirements.txt`
- Re-run `playwright install chromium` if browser-based ingestion fails

---

## Future Enhancements

The following upgrades would make the project more powerful, scalable, and production-ready:

- Add user authentication and role-based access for different agricultural stakeholders
- Support multilingual query handling beyond English and Tamil, including regional dialects
- Integrate real-time weather data and crop advisory recommendations
- Add a dashboard with crop health, soil health, and seasonal insights
- Enable voice-based interaction for farmers using speech-to-text and text-to-speech
- Add automatic document refresh and scheduled index updates for new scheme information
- Improve retrieval quality with hybrid search using semantic and keyword-based ranking
- Add citation and source highlighting so users can see which document informed the answer
- Store uploaded files and metadata in a database instead of only the local file system
- Support more file formats such as DOCX, CSV, images, and scanned documents
- Add an admin panel to manage uploaded documents, vector index status, and model settings
- Build a mobile-friendly interface for field use by farmers and rural users
- Deploy the application using Docker and cloud hosting for public or enterprise access
- Add feedback collection so the assistant can improve based on user ratings and corrections

---

## License

This project is intended for educational and demonstration purposes.
" 
