import os
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

load_dotenv()
app = FastAPI()

FAISS_PATH = "faiss_index"

class QueryRequest(BaseModel):
    prompt: str
    temperature: float = 0.7

@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    try:
        all_docs = []
        os.makedirs("Documents", exist_ok=True)
        
        for file in files:
            file_path = os.path.join("Documents", file.filename)
            #Writing file to file_path 
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            
            # Select loader based on file extension,open and parse the file  saved on Documents
            if file.filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file.filename.endswith(".txt"):
                loader = TextLoader(file_path)
            else:
                continue
            #Loader
            docs = loader.load()
            all_docs.extend(docs)
        
        if not all_docs:
            raise HTTPException(status_code=400, detail="No valid documents processed.")
        
        # Textsplitter
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        # Split text into chunks
        chunks = text_splitter.split_documents(all_docs)
        
        # Embedding
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vectorstore = FAISS.from_documents(chunks, embeddings)
        #Save Vector- on Persist
        if os.path.exists(FAISS_PATH):
            #Adds chunks if exist
            vectorstore = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
            vectorstore.add_documents(chunks)  
        else:
            vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(FAISS_PATH)
        print(f"Successfully indexed {len(chunks)} chunks from {len(files)} file(s).")
        if vectorstore is not None:
            print("Total chunks in FAISS:", vectorstore.index.ntotal)

            all_sources = {doc.metadata.get("source")
                    for doc in vectorstore.docstore._dict.values()
                    }
        print("Files currently indexed in FAISS:", all_sources)
        return{"message":f"Files { ", ".join([f.filename for f in files])} uploaded successfully"}
        
               
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
def generate_response(query: QueryRequest):
    try:
        local_context = "No documents uploaded yet."
        
        # retrieve from vectorDB
        if os.path.exists(FAISS_PATH):
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            vectorstore = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
            #Search Vector Store and get results
            retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
            relevant_docs = retriever.invoke(query.prompt)
            local_context = "\n".join([doc.page_content for doc in relevant_docs])
        
        #Instruct the LLM to behave as a assisitant for Agri queries only
        system_prompt = (
            "You are an expert agricultural AI assistant. Respond in the following language: {query.language}. "
            "Your task is to answer questions strictly related to agriculture, farming, crops, soil, irrigation, pests, fertilizers, or agricultural government schemes using the uploaded document context below.\n\n"
            "CRITICAL RULE: If the user's question is NOT related to agriculture, farming, or rural/crop management, you must refuse to answer and state clearly: "
            "'This question is not related to agriculture.' (If the requested language is Tamil, translate this refusal into natural Tamil).\n\n"
            f"--- Uploaded Document Context ---\n{local_context}"
        )
        #Retrive from LLM
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=query.temperature)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query.prompt)
        ]
        #Search LLM
        ai_response = llm.invoke(messages)
        return {"response": ai_response.content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))