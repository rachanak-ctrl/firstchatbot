import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = InMemoryChatMessageHistory()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help you today?"}
    ]

# 1. Initialize ChatGoogleGenerativeAI using Gemini 3.5 Flash
# It automatically reads your key from Streamlit Secrets or Environment Variables
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=st.secrets.get("GEMINI_API_KEY"),
    temperature=0.7
)

# Create a prompt template with message history
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Have a natural conversation with the user."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Create the chain
chain = prompt_template | llm

# Function to get session history
def get_session_history() -> BaseChatMessageHistory:
    return st.session_state.chat_history

# Create runnable with message history
conversation = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# Create user interface
st.title("🗣️ Conversational Chatbot")
st.subheader("Simple Chat Interface for LLMs by Build Fast with AI")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if user_input := st.chat_input("Your question"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Invoke the conversation chain
            response = conversation.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": "default"}}
            )
            
            # Extract content from AIMessage
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            st.write(response_content)
            
            # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": response_content})
