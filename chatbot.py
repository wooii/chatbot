"""
Created on Sat Jun  1 10:43:58 2024
@author: Chenfeng Chen
"""

from openai import OpenAI
import streamlit as st

# Prices per 1M tokens
prices_per_1M_tokens = {
    "gpt-4o": {"input": 5, "output": 15},
    "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
}

class Chat:
    def __init__(self, model: str = "gpt-3.5-turbo", max_tokens: int = 1000, top_p: float = 0.1, number_of_responses: int = 1):
        self.model = model
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.n = number_of_responses
        self.messages = [{"role": "system", "content": "be concise, use python"}]
        self.price_for_1_input_token = prices_per_1M_tokens[model]["input"] / 1e6
        self.price_for_1_output_token = prices_per_1M_tokens[model]["output"] / 1e6

    def chat_loop(self, client, user_message):
        self.messages.append({"role": "user", "content": user_message})
        response = client.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            n=self.n
        )
        answer = response.choices[0].message["content"]
        self.messages.append({"role": "assistant", "content": answer})
        return answer, response.usage["prompt_tokens"], response.usage["completion_tokens"]

    def calculate_cost(self, n_input_tokens, n_output_tokens):
        cost_input = self.price_for_1_input_token * n_input_tokens
        cost_output = self.price_for_1_output_token * n_output_tokens
        return cost_input + cost_output

# Sidebar for API key and model selection
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")

    selected_model = st.selectbox("Select Model", options=["gpt-3.5-turbo", "gpt-4o"])

# Initialize chat instance
if "chat_instance" not in st.session_state:
    st.session_state["chat_instance"] = Chat(model=selected_model)

# Display title and previous messages
st.title("Chatbot")
st.caption(f"A chatbot powered by OpenAI ({selected_model})")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Get user input and generate response
if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    chat_instance = st.session_state["chat_instance"]

    answer, n_input_tokens, n_output_tokens = chat_instance.chat_loop(client, prompt)
    cost = chat_instance.calculate_cost(n_input_tokens, n_output_tokens)

    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    st.session_state["messages"].append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)

    st.write(f"Cost for this query: ${cost:.6f}.")

