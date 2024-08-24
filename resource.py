import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_models import ChatOpenAI

# Load environment variables from .env file
llm_name = "gpt-3.5-turbo"

# Create the directory for the vector database if it doesn't exist
vectoredb_dir = os.path.join(os.getcwd(), 'db', 'chroma')
os.makedirs(vectoredb_dir, exist_ok=True)
chat_history = []


def initialize_api():
    # Check if the OpenAI API key is loaded
    load_dotenv(find_dotenv())
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        return None
    else:
        return "success"


def load_split_pdf(file_path):
    try:
        # Load PDF documents
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        splits = text_splitter.split_documents(documents)

        # Define embeddings using OpenAI
        embeddings = OpenAIEmbeddings()

        # Create or load the vector database
        vectordb = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=vectoredb_dir
        )

        # Persist the database to disk
        vectordb.persist()

        # Check if the vector database contains embeddings
        if vectordb._collection.count():
            # Return the file path if the embeddings were successfully created
            return file_path

        # Return None if the embeddings were not created successfully
        return None

    except Exception as ex:
        # print(f"Error during embeddings creation: {ex}")
        return None


def load_query(files):
    persist_directory = vectoredb_dir
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    # define retriever
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 3}, filter={"source":"extract the answer only from this listed documents and should only be referenced as the source document. "+", ".join(files)})
    # create a chatbot chain. Memory is managed externally.
    qa = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model_name=llm_name, temperature=0),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    return qa

def get_sources(doc_ref):
    """
    Processes documents stored in `self.db_response` to extract unique metadata
    and returns a formatted string of page and source information.

    Returns:
        str: A string formatted with unique page and source information from documents.
    """
    if not doc_ref:
        return ""

    unique_metadata = {}
    for doc in doc_ref:
        metadata = doc.metadata
        source = os.path.basename(str(metadata['source']))
        page = metadata['page']
        metadata_key = f"{source}_{page}"

        if metadata_key not in unique_metadata:
            unique_metadata[metadata_key] = (page, source)

    response_parts = [f"Page: {info[0]}; Source: {info[1]}" for info in unique_metadata.values()]
    return ", ".join(response_parts)


def message_handler(query, source_files):
    if not query:
        return 'No Chat History'
    qa = load_query(source_files)
    result = qa({"question": query, "chat_history": chat_history})
    chat_history.extend([(query, result["answer"])])
    doc_ref = result["source_documents"]
    answer = result['answer']
    return f"Chatbot: \n{str(answer)}", str(get_sources(doc_ref))
