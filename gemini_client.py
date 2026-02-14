import google.generativeai as genai
from prompts import get_strict_system_prompt
import os

class GeminiClient:
    def __init__(self, api_key, model_name="gemini-2.0-flash"):
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.generation_config = {
            "temperature": 0.0, # Set to 0 for maximum determinism
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 8192,
        }
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

    def get_chat_response(self, chat_history, context_text, user_input):
        """
        Generates a response using the Gemini model with the strict system prompt.
        Note: For RAG with strict context, we often construct a new chat session 
        or pass the system prompt dynamically for each turn if the context changes.
        Here we assume context is static per session or updated.
        """
        
        system_instruction = get_strict_system_prompt(context_text)
        
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
            system_instruction=system_instruction
        )

        # Convert Streamlit chat history to Gemini format if needed
        # But for simplicity with system_instruction, we can just send the chat history
        # Gemini handles history via start_chat or list of contents
        
        history_for_gemini = []
        for msg in chat_history:
            role = "user" if msg["role"] == "user" else "model"
            history_for_gemini.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=history_for_gemini)
        
        try:
            response = chat.send_message(user_input)
            return response.text
        except Exception as e:
            return f"에러가 발생했습니다: {str(e)}"
