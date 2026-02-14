# 🔦 Light RAG Chatbot - 프로젝트 인수인계 가이드

## 1. 프로젝트 개요 (Project Overview)

이 프로젝트는 **교회 조명팀(LOGOS)**을 위해 설계된 **RAG (검색 증강 생성) 챗봇**입니다.
주목적은 신입 팀원이나 봉사자들이 제공된 매뉴얼("조명에대한모든것.md")에 기반한 답변을 통해 조명 콘솔 운영, 전원 관리 및 기타 기술적인 내용을 쉽게 이해하도록 돕는 것입니다.

**유형:** Streamlit 웹 애플리케이션
**AI 모델:** Google Gemini 2.0 Flash

## 2. 현재 상태 (Current Status)

이 프로젝트는 완전히 기능하는 프로토타입입니다.

- **핵심 로직:** 구현 완료. 시스템 프롬프트에 문서 내용을 포함시켜 Gemini가 해당 내용에 기반해서만 답변하도록 지시합니다.
- **UI:** Streamlit을 사용하여 구현 완료. 채팅 인터페이스와 파일 관리를 위한 관리자 사이드바를 포함합니다.
- **데이터 소스:** 현재 로컬 마크다운 파일인 `조명에대한모든것.md`를 기본 지식 베이스로 사용합니다. 관리자가 PDF/TXT/MD 파일을 동적으로 업로드하여 변경할 수 있습니다.

## 3. 기술 스택 (Technology Stack)

- **언어:** Python 3.x
- **프레임워크:** Streamlit
- **LLM:** Google Gemini API (`google-generativeai`)
- **주요 라이브러리:**
  - `pdfplumber`: PDF 업로드 시 텍스트 추출용.
  - `python-dotenv`: 로컬 환경 변수 관리용.

## 4. 주요 기능 (Key Features)

1.  **엄격한 RAG (Strict RAG):**
    - 봇은 제공된 참조 텍스트에 _기반해서만_ 답변하도록 엄격하게 지시받았습니다.
    - 매뉴얼에 없는 일반 상식 질문에는 답변을 거부합니다.
2.  **관리자 모드 (Admin Mode):**
    - `ADMIN_PASSWORD`로 보안 설정됨.
    - 새로운 매뉴얼(PDF/TXT/MD)을 업로드하여 세션의 컨텍스트를 동적으로 교체할 수 있습니다.
3.  **유연한 설정 (Flexible Configuration):**
    - API 키와 비밀번호를 UI 입력, `.env` 파일, 또는 Streamlit Secrets(클라우드 배포용)를 통해 설정할 수 있습니다.

## 5. 파일 구조 (File Structure)

- `app.py`: 메인 진입점. UI, 상태 관리 및 전체 조정을 담당합니다.
- `gemini_client.py`: Gemini API 상호작용을 위한 래퍼 클래스. 설정 및 안전 설정을 처리합니다.
- `prompts.py`: 엄격한 컨텍스트 준수를 강제하는 시스템 프롬프트 로직을 포함합니다.
- `조명에대한모든것.md`: 조명 매뉴얼이 포함된 기본 지식 베이스 파일입니다.
- `.env`: (선택 사항) 로컬 환경 변수 (`GOOGLE_API_KEY`, `ADMIN_PASSWORD`)

## 6. 실행 방법 (How to Run)

### 필수 조건

- Python 설치.
- Gemini용 Google Cloud API 키.

### 설치

```bash
# 가상 환경 생성 (권장)
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate  # Windows

# 의존성 패키지 설치
pip install -r requirements.txt
```

### 앱 실행

```bash
streamlit run app.py
```

## 7. 설정 가이드 (에이전트용)

새로운 환경이나 에이전트로 이동할 때:

1.  **API 키:** 환경 변수 또는 `.streamlit/secrets.toml`에 `GOOGLE_API_KEY`가 설정되어 있는지 확인하세요.
2.  **관리자 비밀번호:** 파일 업로드 기능을 보호하기 위해 `ADMIN_PASSWORD`를 설정하세요.

## 8. 로직 상세 (개발자용)

- **프롬프트 엔지니어링 (`prompts.py`):**
  - `get_strict_system_prompt` 함수는 전체 문서 내용을 시스템 프롬프트에 주입합니다.
  - 외부 지식 사용을 명시적으로 금지하며, 정보가 없을 경우 모른다고 답하도록 요구합니다.
- **Gemini 상호작용 (`gemini_client.py`):**
  - `gemini-2.0-flash` 모델 사용.
  - 최대의 결정론적 답변을 위해 Temperature를 `0.0`으로 설정.
  - 현재 컨텍스트와 엄격한 시스템 프롬프트가 항상 활성화되도록 매 턴마다 채팅 세션 로직을 재초기화합니다.

## 9. 향후 개선 사항 (Future Improvements)

- **청킹 (Chunking):** 현재는 전체 문서를 컨텍스트 창에 전달합니다. 매우 큰 매뉴얼의 경우 벡터 데이터베이스 검색(RAG) 구현이 필요할 수 있습니다.
- **영구 저장 (Persistence):** 업로드된 파일은 영구 저장되지 않고 세션 레벨에서만 유지됩니다.
- **배포 (Deployment):** Streamlit Cloud 배포 준비 완료 상태입니다.
