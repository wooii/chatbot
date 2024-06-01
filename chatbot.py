"""
Created on Sat Jun  1 10:43:58 2024
@author: Chenfeng Chen
"""
from openai import OpenAI
import streamlit as st

prices_per_1M_tokens = {
    "gpt-4o":          {"input": 5,   "output": 15},
    "gpt-3.5-turbo":   {"input": 0.5, "output": 1.5},
}

# Sidebar for API key and model selection
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")

    selected_model = st.selectbox(
        "Select Model",
        options=["gpt-3.5-turbo", "gpt-4o"]
    )



# Initialize messages and store selected model
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
if "model" not in st.session_state:
    st.session_state["model"] = selected_model

# Display title and previous messages
st.title("Chatbot")
st.caption(f"A chatbot powered by OpenAI ({st.session_state.model})")

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Get user input and generate response
if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Update prices based on the selected model before calculating the cost
    price_for_1_input_token = prices_per_1M_tokens[st.session_state.model]["input"] / 1e6
    price_for_1_output_token = prices_per_1M_tokens[st.session_state.model]["output"] / 1e6

    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model=st.session_state.model,  # Use the selected model
        messages=st.session_state.messages,
        max_tokens=1000,
    )
    n_input_tokens = response.usage.prompt_tokens
    n_output_tokens =  response.usage.completion_tokens
    cost_input = price_for_1_input_token*n_input_tokens
    cost_output = price_for_1_output_token*n_output_tokens
    total_cost = cost_input + cost_output

    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
    st.write(f"Using {st.session_state.model}, cost for this query: ${total_cost:.6f}")
