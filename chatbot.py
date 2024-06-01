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
    prices_per_1M_tokens = prices_per_1M_tokens

    def __init__(self, model: str = "gpt-3.5-turbo", max_tokens: int = 1000, top_p: float = 0.1,
                 number_of_responses: int = 1, use_chat_history: bool = False):
        self.model = model
        self.top_p = top_p
        self.n = number_of_responses
        self.max_tokens = max_tokens
        self.use_chat_history = use_chat_history
        self.price_for_1_input_token = self.prices_per_1M_tokens[self.model]["input"] / 1e6
        self.price_for_1_output_token = self.prices_per_1M_tokens[self.model]["output"] / 1e6
        self.is_initial_prompt = True
        self.messages = []
        self.instruction = {"role": "system", "content": "be concise, use python"}
        self.response = None

    def chat_loop(self, client):
        if len(self.messages[-1]["content"]) > 0:
            self.response = client.ChatCompletion.create(
                model=self.model,
                messages=self.messages,
                top_p=self.top_p,
                n=self.n,
                max_tokens=self.max_tokens,
            )
            self._parse_response()
            self._save_chat()

        else:
            print("Got no input.")

    def chat(self, client):
        self._get_messages()
        self.chat_loop(client)

    def _prompt(self):
        return input("Enter a prompt here:\n")

    def _get_messages(self):
        prompt = self._prompt()
        self.messages.append({"role": "user", "content": prompt})
        if self.is_initial_prompt:
            self.messages = [self.instruction, self.messages[0]]
            self.is_initial_prompt = False

    def _parse_response(self):
        if self.response is not None:
            self.answer = self.response.choices[0].message["content"]
            self.role = self.response.choices[0].message["role"]
            self.messages.append({"role": self.role, "content": self.answer})
            print(f"{self.role}: \n{self.answer}")
            n_input_tokens = self.response.usage["prompt_tokens"]
            n_output_tokens = self.response.usage["completion_tokens"]
            cost_input = self.price_for_1_input_token * n_input_tokens
            cost_output = self.price_for_1_output_token * n_output_tokens
            print(f"Cost for this query: ${(cost_input + cost_output):.6f}.")


# Sidebar for API key and model selection
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")

    selected_model = st.selectbox("Select Model", options=["gpt-3.5-turbo", "gpt-4o"])

# Initialize messages and store selected model
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
if "model" not in st.session_state:
    st.session_state["model"] = selected_model
if "chat_instance" not in st.session_state:
    st.session_state["chat_instance"] = Chat(model=st.session_state["model"])

# Display title and previous messages
st.title("Chatbot")
st.caption(f"A chatbot powered by OpenAI ({st.session_state.model})")

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Get user input and generate response
if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    client = OpenAI(api_key=openai_api_key)

    # Update the Chat instance and get response
    st.session_state["chat_instance"].model = st.session_state.model
    st.session_state["chat_instance"].messages = st.session_state.messages
    st.session_state["chat_instance"].chat_loop(client)
    msg = st.session_state["chat_instance"].answer
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
