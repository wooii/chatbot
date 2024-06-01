"""
Created on Sat Jun  1 10:43:58 2024
@author: Chenfeng Chen
"""
from openai import OpenAI
import streamlit as st

class ChatbotApp:
    def __init__(self):
        self.prices_per_1M_tokens = {
            "gpt-4o":          {"input": 5,   "output": 15},
            "gpt-3.5-turbo":   {"input": 0.5, "output": 1.5},
        }
        self.initialize_session_state()
        self.setup_sidebar()
        self.display_chat()

    def initialize_session_state(self):
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
        if "model" not in st.session_state:
            st.session_state["model"] = "gpt-3.5-turbo"

    def setup_sidebar(self):
        with st.sidebar:
            self.openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
            st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")

            selected_model = st.selectbox(
                "Select Model",
                options=["gpt-3.5-turbo", "gpt-4o"],
                index=0,
                key="selected_model"
            )

        if st.session_state["model"] != selected_model:
            st.session_state["model"] = selected_model

    def display_chat(self):
        st.title("Chatbot")
        st.caption("A chatbot powered by OpenAI.")

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input():
            self.process_user_input(prompt)

    def process_user_input(self, prompt):
        if not self.openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        price_for_1_input_token = self.prices_per_1M_tokens[st.session_state["model"]]["input"] / 1e6
        price_for_1_output_token = self.prices_per_1M_tokens[st.session_state["model"]]["output"] / 1e6

        client = OpenAI(api_key=self.openai_api_key)
        response = client.chat.completions.create(
            model=st.session_state["model"],
            messages=st.session_state["messages"],
            max_tokens=1000,
        )
        n_input_tokens = response.usage.prompt_tokens
        n_output_tokens = response.usage.completion_tokens
        cost_input = price_for_1_input_token * n_input_tokens
        cost_output = price_for_1_output_token * n_output_tokens
        total_cost = cost_input + cost_output

        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
        st.write(f"Using {st.session_state['model']}, cost for this query: ${total_cost:.6f}")

if __name__ == "__main__":
    ChatbotApp()
