import streamlit as st
import requests

st.set_page_config(page_title="Agri Assist", page_icon="🌱", layout="wide")

# Initialize chat history in session state so it persists across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for file uploads & settings
with st.sidebar:
    st.caption("Agri Knowledge Hub")
    st.divider()
    st.markdown("📚 Upload agricultural documents to query them instantly.")
    st.header("Document Upload")
    
    uploaded_files = st.file_uploader(
        "Upload PDF or TXT files",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )
    
    if st.button("Process & Index Files"):
        if uploaded_files:
            with st.spinner("Uploading and indexing documents on backend..."):
                try:
                    files_payload = [
                        ("files", (file.name, file.getvalue(), file.type))
                        for file in uploaded_files
                    ]
                    
                    res = requests.post("http://localhost:8000/upload", files=files_payload)
                    
                    if res.status_code == 200:
                        file_names = ", ".join([f.name for f in uploaded_files])
                        #st.success("Uploaded")
                        #st.success(f"Successfully uploaded: {file_names}!")
                        st.info(res.json().get("message"))
                        #To clear the inputs
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to FastAPI backend. Ensure uvicorn is running on port 8000.")
        else:
            st.warning("Please select at least one file first.")
            
    st.divider()
    temperature = 0.5
    st.markdown("### 🌐 Language")
    selected_language = st.selectbox(
        "Choose your language",
        ["English", "தமிழ் (Tamil)"]
    )

# Main Chat Interface Header
st.markdown("""
<div class="header">
    <h1>🌱 Agricultural AI Assistant</h1>
    <p>Your smart farming companion | உங்கள் விவசாய நண்பன்</p>
</div>
""", unsafe_allow_html=True)

# Display prior chat messages from session state on every rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box at the bottom of the screen
if prompt := st.chat_input("Ask a question about crop cultivation, pests, irrigation, or schemes..."):
    # 1. Save and display user message
    st.session_state.messages.append({"role": "user", "avatar":"🧑‍🌾","content": prompt})
    with st.chat_message("user",avatar="🧑‍🌾"):
        st.markdown(prompt)

    # 2. Query FastAPI backend
    with st.chat_message("assistant",avatar="🌱"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    "http://localhost:8000/generate",
                    json={
                        "prompt": prompt,
                        "temperature": temperature,
                        "language": selected_language
                    }
                )
                
                if response.status_code == 200:
                    answer = response.json().get("response")
                    st.markdown(answer)
                    # 3. Save assistant response to session history
                    st.session_state.messages.append({"role": "assistant","avatar":"🌱","content": answer})
                else:
                    error_msg = f"Error {response.status_code}: {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant","avatar":"🌱", "content": error_msg})
                    
            except requests.exceptions.ConnectionError:
                error_msg = "Cannot connect to FastAPI backend. Make sure Uvicorn is running on port 8000."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "avatar":"🌱","content": error_msg})