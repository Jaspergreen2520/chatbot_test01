import streamlit as st
import google.generativeai as genai

# Show title and description.
st.title("💬 Chatbot (Gemini)")
st.write(
    "このチャットボットはGoogle Gemini Proモデルを使用して応答を生成します。"
    "利用するにはGemini APIキーが必要です。APIキーは [Google AI Studio](https://aistudio.google.com/app/apikey) で取得できます。"
    "OpenAI版のチュートリアルは [こちら](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps) を参照できます。"
)

# Ask user for their Gemini API key via `st.text_input`.
gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Gemini APIキーを入力してください。", icon="🗝️")
else:
    # Set API key for Google Generative AI
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-pro")

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message.
    if prompt := st.chat_input("なんでも聞いてください！"):
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini API: Prepare messages as context for the model
        history = []
        for m in st.session_state.messages:
            if m["role"] == "user":
                history.append({"role": "user", "parts": [m["content"]]})
            elif m["role"] == "assistant":
                history.append({"role": "model", "parts": [m["content"]]})

        # Generate a response using Gemini API
        response = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": 2048},
            stream=True,
            safety_settings=[{"category": "HARM_CATEGORY_DEROGATORY", "threshold": "BLOCK_NONE"}],
            # Optionally add context/history if you want multi-turn
        )

        # Stream the response to the chat using `st.write_stream`, then store it in session state.
        with st.chat_message("assistant"):
            reply = st.write_stream(response)
        st.session_state.messages.append({"role": "assistant", "content": reply})
