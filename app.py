import streamlit as st
import os
import pdfplumber
from gemini_client import GeminiClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Light RAG Chatbot", layout="wide")

st.title("LOGOS 조명팀 chatbot")

# Sidebar for configuration
with st.sidebar:
    st.header("설정")
    
    # API Key Input
    # Priority: 1. User Input, 2. OS Env (including .env), 3. Streamlit Secrets
    api_key = st.text_input("Google API Key 입력", type="password", help="Google AI Studio에서 발급받은 키를 입력하세요.")
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            if "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]


    st.divider()
    
    # File Uploader (Admin Only)
    uploaded_file = None
    
    # Check for admin password
    admin_password = st.text_input("관리자 암호 (파일 업로드용)", type="password")
    is_admin = False
    
    # Check env/secrets for password (default to 'admin' if not set for testing, but recommend setting it)
    correct_password = os.getenv("ADMIN_PASSWORD") 
    if not correct_password and "ADMIN_PASSWORD" in st.secrets:
        correct_password = st.secrets["ADMIN_PASSWORD"]
        
    if correct_password and admin_password == correct_password:
        is_admin = True
        st.success("관리자 확인됨")
    
    if is_admin:
        uploaded_file = st.file_uploader("문서 업로드 (PDF/TXT)", type=["pdf", "txt", "md"])
    else:
        st.info("파일 업로드는 관리자만 가능합니다. (기본 문서 사용)")

    context_text = ""
    # 1. Try to load default file if no upload
    default_file_path = "조명에대한모든것.md"
    if not uploaded_file and os.path.exists(default_file_path):
        try:
            with open(default_file_path, "r", encoding="utf-8") as f:
                context_text = f.read()
            if is_admin: # Only show this info to admin to avoid clutter
                st.info(f"기본 문서 '{default_file_path}'가 로드되었습니다. ({len(context_text)} 자)")
        except Exception as e:
            st.error(f"기본 문서 로드 실패: {e}")

    # 2. Overwrite with uploaded file if exists
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                pages = [page.extract_text() for page in pdf.pages]
                context_text = "\n".join(filter(None, pages))
        else: # txt or md
            context_text = uploaded_file.read().decode("utf-8")
        
        st.success(f"새로운 문서 로드 완료! ({len(context_text)} 자)")
    
    if context_text:
        with st.expander("로드된 텍스트 확인"):
            st.text(context_text[:1000] + "...")
    else:
        st.info("문서를 업로드하면 대화를 시작할 수 있습니다.")

# Chat Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("질문을 입력하세요..."):
    if not api_key:
        st.error("API 키가 필요합니다.")
    elif not context_text:
        st.error("먼저 문서를 업로드해주세요.")
    else:
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant message
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("생성 중...")
            
            client = GeminiClient(api_key=api_key)
            # Pass history excluding the latest prompt which is handled by send_message inside client (or handle properly)
            # Correction: client.get_chat_response takes history excluding current prompt usually, or we pass valid history.
            # In my client implementation, I passed the history including current prompt? No, let's check.
            # Client code: history_for_gemini = from chat_history. chat.send_message(user_input).
            # So we pass previous messages.
            
            current_history = st.session_state.messages[:-1] # Exclude the just added user prompt
            response_text = client.get_chat_response(current_history, context_text, prompt)
            
            message_placeholder.markdown(response_text)
            
        st.session_state.messages.append({"role": "assistant", "content": response_text})
