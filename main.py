import logging
import streamlit as st
import uuid
import openai

from services.embedding_service import EmbeddingService
from services.vectorestore_service import VectorStoreService
from services.query_service import QueryService

from utils.error_management import get_friendly_error_message


logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def initialize_vectorstore():
    """Initialize Pinecone vectorstore with dependency injection."""
    embedding_service = EmbeddingService()
    vector_storeService = VectorStoreService(embedding_service)
    query_service = QueryService(vector_storeService)

    return embedding_service, vector_storeService, query_service


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = str(uuid.uuid4())


def display_chat_history():
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def format_references(matching_docs):
    if not matching_docs:
        return ""

    references = []
    for i, doc in enumerate(matching_docs, 1):
        source = doc.metadata.get("source", f"Document {i}")
        page = doc.metadata.get("page", f"{int(float(doc.metadata["page_number"]))}")
        # get the entire paragraph
        doc_text = f"""
            Reference {i}:
            - Source: {source}
            - Page: {page}

            Excerpt:
            > {doc.page_content}
            """
        references.append(doc_text)

    return "\n".join(references)


def main():
    st.set_page_config(
        page_title="Cameroon Tax Assistant", page_icon="🔹", layout="centered"
    )
    st.markdown(
        """
                <style>
    .reportview-container {
        background-color: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2980b9;
        color: white;
        transform: scale(1.05);
    }
    </style>
                """, unsafe_allow_html=True
    )
    st.title("Cameroon Tax Assistant")
    st.markdown("*Your intelligent guide to navigating Cameroon's tax landscape*")

    try:
        embedding_service, vector_storeService, query_service = initialize_vectorstore()
        initialize_session_state()
    except Exception as e:
        st.error(f"Failed to initialize services: {e}")
        return

    with st.sidebar:
        st.header("Quick Start Guide")
        st.info(
            """
        💡**Tips**:
        - Ask specific tax-related questions
        - Provide context for better answers
        - Explore various tax topics
        """
        )
        st.header("Conversation Starters")
        conversation_starters = [
            "What are the key tax regulations for businesses in Cameroon?",
            "Can you explain personal income tax rates?",
            "What tax deductions are available for small businesses?",
            "How do corporate tax structures work in Cameroon?",
            "What are the tax obligations for foreign companies?",
        ]
        for starter in conversation_starters:
            if st.button(starter):
                st.session_state.messages.append({"role": "user", "content": starter})
                st.rerun()

    display_chat_history()

    if prompt := st.chat_input("Ask any tax-related question"):

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                st.markdown("bot")
                try:
                    retrieved_docs = query_service.process_query(prompt)
                    response = query_service.generate_response(retrieved_docs, prompt)

                    st.markdown(response)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                    with st.expander("Reference Documents"):
                        for doc in retrieved_docs:
                            formatted_refs = format_references(retrieved_docs)
                            st.markdown(formatted_refs)
                except openai.APIConnectionError as e:
                    error_msg = get_friendly_error_message(e)
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )
                except Exception as e:
                    error_msg = get_friendly_error_message(e)
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )
                    logger.error(f"Error in chat processing: {e}")
                    raise


main()
