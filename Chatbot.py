import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Initialize session state for chat history tracking
if "chat_history" not in st.session_state:
    st.session_state.chat_history = InMemoryChatMessageHistory()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help you today?"}
    ]

# 1. Initialize ChatGoogleGenerativeAI using Gemini 3.5 Flash
# It will read the key securely from your Streamlit Secrets
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=st.secrets.get("GEMINI_API_KEY"),
    temperature=0.7
)

# 2. Create a prompt template with message history placeholders
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Have a natural conversation with the user."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# 3. Create the execution chain
chain = prompt_template | llm

# Function to pull session history state
def get_session_history() -> BaseChatMessageHistory:
    return st.session_state.chat_history

# 4. Create a runnable that binds the chain with persistent memory history
conversation = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# 5. Build the user interface layout
st.title("🗣️ Conversational Chatbot")
st.subheader("Simple Chat Interface for LLMs by Build Fast with AI")

# Display past chat history messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. Capture and handle fresh user input
if user_input := st.chat_input("Your question"):
    # Append user message to display array and present it on UI
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # Generate response block
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Execute the LangChain pipeline
            response = conversation.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": "default"}}
            )
            
            # 7. Strict Parsing: Strip away type wrappers, JSON formats, or streaming indices
            if hasattr(response, 'content'):
                response_content = response.content
            elif isinstance(response, dict) and 'content' in response:
                response_content = response['content']
            elif isinstance(response, dict) and 'text' in response:
                response_content = response['text']
            else:
                response_content = str(response)
            
            # Print only clean, beautiful markdown text to the screen
            st.write(response_content)
            
            # Save the clean message text into history
            st.session_state.messages.append({"role": "assistant", "content": response_content})
