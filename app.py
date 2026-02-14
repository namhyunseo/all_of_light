import streamlit as st
import os
import pdfplumber
from gemini_client import GeminiClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Light RAG Chatbot", page_icon="💡", layout="wide")

# Custom CSS Loading
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load CSS if it exists
css_file = "style.css"
if os.path.exists(css_file):
    local_css(css_file)

st.title("💡 LOGOS 조명팀 Chatbot")
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ 설정")
    
    # API Key Input
    with st.expander("🔑 API Key 설정", expanded=False):
        api_key = st.text_input("Google API Key", type="password", help="Google AI Studio 키 입력")
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key and "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
    
    st.divider()
    
    # Clear Chat Button
    if st.button("🗑️ 대화 내용 지우기", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    
    # File Upload Section
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    with st.expander("📂 문서 관리 (관리자 전용)", expanded=st.session_state.admin_authenticated):
        if not st.session_state.admin_authenticated:
            admin_password = st.text_input("관리자 암호", type="password")
            correct_password = os.getenv("ADMIN_PASSWORD")
            if not correct_password and "ADMIN_PASSWORD" in st.secrets:
                correct_password = st.secrets["ADMIN_PASSWORD"]
            
            if correct_password and admin_password == correct_password:
                st.session_state.admin_authenticated = True
                st.rerun()
        
        uploaded_file = None
        if st.session_state.admin_authenticated:
            st.success("관리자 권한 인증됨")
            uploaded_file = st.file_uploader("문서 업로드 (PDF/TXT)", type=["pdf", "txt", "md"])
        else:
            st.info("문서 업로드를 위해 관리자 암호를 입력하세요.")

    # Context Loading Logic
    context_text = ""
    default_file_path = "조명에대한모든것.md"
    
    # 1. Load default file if available & no upload
    if not uploaded_file and os.path.exists(default_file_path):
        try:
            with open(default_file_path, "r", encoding="utf-8") as f:
                context_text = f.read()
            # Show loaded document info in sidebar
            st.success(f"✅ 기본 문서 로드됨\n({os.path.basename(default_file_path)})")
        except Exception as e:
            st.error(f"❌ 기본 문서 로드 실패: {e}")

    # 2. Overwrite with uploaded file
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                pages = [page.extract_text() for page in pdf.pages]
                context_text = "\n".join(filter(None, pages))
        else:
            context_text = uploaded_file.read().decode("utf-8")
        st.success(f"✅ 업로드 문서 로드됨\n({uploaded_file.name})")
    
    if context_text:
        with st.expander("📝 로드된 텍스트 미리보기"):
            st.text(context_text[:500] + "...")
    else:
        st.warning("⚠️ 로드된 문서가 없습니다.")

# Chat Logic initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    role = message["role"]
    avatar = "👤" if role == "user" else "💡"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("조명 팀에 대해 궁금한 점을 물어보세요..."):
    if not api_key:
        st.error("🚨 API 키가 설정되지 않았습니다.")
    elif not context_text:
        st.error("🚨 질문에 답변할 문서(Context)가 없습니다.")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant", avatar="💡"):
            message_placeholder = st.empty()
            message_placeholder.markdown("⏳ 답변 생성 중...")
            
            try:
                client = GeminiClient(api_key=api_key)
                # Pass history excluding current prompt
                current_history = st.session_state.messages[:-1]
                response_text = client.get_chat_response(current_history, context_text, prompt)
                message_placeholder.markdown(response_text)
                
                # Add assistant message to history
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                message_placeholder.error(f"오류가 발생했습니다: {str(e)}")
