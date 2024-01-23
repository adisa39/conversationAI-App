import os

from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import DocArrayInMemorySearch, Chroma
from langchain.document_loaders import TextLoader
from langchain.chains import RetrievalQA,  ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from dotenv import load_dotenv, find_dotenv
import openai

import datetime
current_date = datetime.datetime.now().date()
if current_date < datetime.date(2023, 9, 2):
    llm_name = "gpt-3.5-turbo-0301"
else:
    llm_name = "gpt-3.5-turbo"
print(llm_name)

_ = load_dotenv(find_dotenv())
openai.api_key = os.environ['OPENAI_API_KEY']


def qa(question):
    # loaders = [PyPDFLoader("docs/" + i.replace(" ", "")) for i in os.listdir("docs")]
    # docs = []
    # for loader in loaders:
    #     docs.extend(loader.load())

    persist_directory = 'docs/chroma/'
    embedding = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
    print(vectordb._collection.count())

    docs = vectordb.similarity_search(question, k=3)
    len(docs)
    llm = ChatOpenAI(model_name=llm_name, temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectordb.as_retriever(),
        #return_generated_question=True,
    )
    result = qa_chain({"query": question})
    return result


def message_handler(msg, display_func):
    result = qa(msg)
    display_func(str(result["result"]))


def file_loader():
    loaders = [PyPDFLoader("docs/" + i.replace(" ", "")) for i in os.listdir("docs") if i.endswith(".pdf")]
    docs = []
    for loader in loaders:
        docs.extend(loader.load())
    return docs


def load_db():
    # load documents
    documents = file_loader()
    # split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)
    # define embedding
    embeddings = OpenAIEmbeddings()
    # create vector database from data
    db = DocArrayInMemorySearch.from_documents(docs, embeddings)
    # define retriever
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    #   for memory
    #memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    # create a chatbot chain. Memory is managed externally.
    qa = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model_name=llm_name, temperature=0),
        #memory=memory,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        return_generated_question=True,
    )
    return qa


# chat_history = []
# query = "what is networking"
# search = load_db()
# # result = search({"question": query, "chat_history": chat_history})
# chat_history.extend([(query, search["answer"])])
# # db_query = search["generated_question"]
# # db_response = search["source_documents"]
# answer = search['answer']
# print(answer)


def upload_file(fn):
    fn = os.path.basename(fn)
    if fn.endswith(".pdf") or fn.endswith(".PDF"):
        output_folder = "docs"
        os.makedirs(output_folder, exist_ok=True)
        try:
            with open(os.path.join(output_folder, fn), 'x') as f:
                f.write(fn)
                print("uploaded successfully \n")
        except FileExistsError:
            print("file uploaded already")
    else:
        print("only pdf file")
