from ast import Try
import os
from datetime import datetime
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="Pranay AI",
    page_icon="",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 1. Powerful Light Theme Custom CSS (Complete Override)
st.markdown(
    """
    <style>
    /* Main Background Force Light */
    .stApp {
        background-color: #f3f4f6 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Elegant Title with Black Gradient */
    .app-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #000000 0%, #444444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 2.5rem;
        letter-spacing: -0.5px;
    }
    
    /* Custom Wrapper Classes for Chat Bubbles */
    .user-bubble {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 20px 20px 4px 20px !important;
        padding: 14px 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        line-height: 1.5;
    }
    
    .assistant-bubble {
        background-color: #e5e7eb !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 20px 20px 20px 4px !important;
        padding: 14px 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
        line-height: 1.5;
    }
    
    /* Input Bar Style Correction */
    div[data-testid="stChatInput"] {
        border-radius: 24px !important;
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.06) !important;
        padding: 4px !important;
    }
    
    div[data-testid="stChatInput"] textarea {
        color: #111827 !important;
    }

    /* Hide Default Clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stChatMessageAvatar"] {display: none !important;} /* Hides default avatar icons for cleaner look */
    </style>
    """,
    unsafe_allow_html=True,
)

# Decorative Title
st.markdown("<h1 class='app-title'> Pranay AI</h1>", unsafe_allow_html=True)

try:
    # Configure Gemini API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("API Key not found! Check your `.env` file.")
        st.stop()

    genai.configure(api_key=api_key)

    # Dynamic Real-time Date/Time Context
    current_now = datetime.now()
    current_date = current_now.strftime("%A, %B %d, %Y")
    current_time = current_now.strftime("%I:%M %p")

    system_instruction = f"""
    You are 'Pranay AI Pro', a premium conversational AI assistant.
    Always answer elegantly, politely, and clearly.
     
     # identity core system instruction  hai

    - You were created and developed by 'Pranay Tembhurkar'.
    - If anyone asks "Who created you?", "Who is your developer?", "Who made you?", "Aapko kisne banaya?", or anything similar, you must proudly and explicitly state that you were created by Pranay Tembhurkar.
    
    
    LIVE CONTEXT:
    - Current Date: {current_date}
    - Current Time: {current_time}
    
    Provide accurate information if asked about the day, date, or time.
    """

    if "final_model" not in st.session_state:
        try:
            available_models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
            flash_model = next((m for m in available_models if "gemini-1.5-flash" in m), None)
            st.session_state.final_model = flash_model if flash_model else (available_models[0] if available_models else "gemini-pro")
        except Exception:
            st.session_state.final_model = "gemini-1.5-flash"

    model = genai.GenerativeModel(
        model_name=st.session_state.final_model,
        system_instruction=system_instruction,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 2. Render History using custom HTML wrappers instead of default broken styles
    for msg in st.session_state.messages:
        bubble_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="{bubble_class}">{msg["content"]}</div>', unsafe_allow_html=True)

    # User Input
    if prompt := st.chat_input("Ask Pranay AI anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)
        
        

        # Assistant Custom Response Container
        response_placeholder = st.empty()
        
        formatted_history = []
        for m in st.session_state.messages[:-1]:
            formatted_history.append({
                "role": "user" if m["role"] == "user" else "model",
                "parts": [m["content"]]
            })

        try:
            chat = model.start_chat(history=formatted_history)
            full_response = ""
            response_stream = chat.send_message(prompt, stream=True)

            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    # Live update inside custom formatted assistant div
                    response_placeholder.markdown(f'<div class="assistant-bubble">{full_response} ▎</div>', unsafe_allow_html=True)

            response_placeholder.markdown(f'<div class="assistant-bubble">{full_response}</div>', unsafe_allow_html=True)

            if full_response:
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.rerun()

        except Exception as api_err:
            st.error(f"Processing Error: {api_err}")

except Exception as global_err:
    st.error(f"System Error: {global_err}")