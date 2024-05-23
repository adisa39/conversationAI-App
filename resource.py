import os
import shutil
from langchain_community.document_loaders import PyPDFLoader

from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import DocArrayInMemorySearch, Chroma
from langchain_community.document_loaders import TextLoader
from langchain.chains import RetrievalQA,  ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
import sys
sys.path.append('../..')
from dotenv import load_dotenv, find_dotenv
import openai

import datetime
current_date = datetime.datetime.now().date()
if current_date < datetime.date(2023, 9, 2):
    llm_name = "gpt-3.5-turbo-0301"
else:
    llm_name = "gpt-3.5-turbo"
# print(llm_name)

_ = load_dotenv(find_dotenv())
openai.api_key = os.environ['OPENAI_API_KEY']


# def qa(question):
#     # loaders = [PyPDFLoader("docs/" + i.replace(" ", "")) for i in os.listdir("docs")]
#     # docs = []
#     # for loader in loaders:
#     #     docs.extend(loader.load())

#     persist_directory = 'docs/chroma/'
#     embedding = OpenAIEmbeddings()
#     vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
#     print(vectordb._collection.count())

#     docs = vectordb.similarity_search(question, k=3)
#     len(docs)
#     llm = ChatOpenAI(model_name=llm_name, temperature=0)
#     qa_chain = RetrievalQA.from_chain_type(
#         llm,
#         retriever=vectordb.as_retriever(),
#         #return_generated_question=True,
#     )
#     result = qa_chain({"query": question})
#     return result


# def message_handler(msg, display_func):
#     result = qa(msg)
#     display_func(str(result["result"]))


# def file_loader():
#     loaders = [PyPDFLoader("docs/" + i.replace(" ", "")) for i in os.listdir("docs") if i.endswith(".pdf")]
#     docs = []
#     for loader in loaders:
#         docs.extend(loader.load())
#     return docs



def loader():
    docs_dir = StorageManager.docs_dir
    loaders = [PyPDFLoader("docs/" + i.replace(" ", "")) for i in os.listdir(docs_dir)]
    docs = []
    for loader in loaders:
        docs.extend(loader.load())
    
    # split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    splits = text_splitter.split_documents(docs)

    # clean previous db
    os.rmdir("./db/chroma")

    # define embedding
    embeddings = OpenAIEmbeddings()
    # create vector database from data
    persist_directory = 'db/chroma/'
    vectordb = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory=persist_directory
    )    
    # print(f"{vectordb._collection.count()} embeddings stored successfully")


class StorageManager: 
    docs_dir = os.path.join(os.getcwd(), "docs")
    vectoredb_dir = os.path.join(os.getcwd(), "db/chroma")

    def show_docs(self):
        filenames = [i for i in os.listdir(self.docs_dir) if i.endswith(".pdf")]
        return filenames

    ''' def upload(self, path):
        """ method to upload file to file storage """
        fn = os.path.basename(path)

        if fn.endswith(".pdf") or fn.endswith(".PDF"):
            os.makedirs(self.docs_dir, exist_ok=True)
            try:
                with open(os.path.join(self.docs_dir, fn.replace(" ", "")), 'x') as f:
                    f.write(path)
                    # print("uploaded successfully \n")
                    # self.show_docs()
            except FileExistsError as err:
                print("file uploaded already")
        else:
            print("only pdf file")
    '''

    def delete_doc(self, files):
        """ method to delete file from storage """
        for file in files:
            print("delete clicked")
            try:
                os.remove(os.path.join(self.docs_dir, file))
                print(f"Deleted {file} successfully\n")
                self.show_docs()
            except FileNotFoundError:
                print(f"File {file} not found")
            except Exception as e:
                print(f"An error occurred: {str(e)}")

    def clear_storage(self):
        # Use shutil.rmtree to remove the directory and all its contents
        if os.path.exists(self.vectoredb_dir):
            shutil.rmtree(self.vectoredb_dir)
            print(f"Removed directory: {self.vectoredb_dir}")
        
        # Handle documents directory separately if needed
        try:
            # Delete all documents in the docs directory
            for file in os.listdir(self.docs_dir):
                file_path = os.path.join(self.docs_dir, file)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            # Optionally remove the docs directory itself if desired
            # os.rmdir(self.docs_dir)
        except Exception as e:
            print(f"Failed to delete files in {self.docs_dir}: {e}")


def load_db(files):
    # Build prompt
    template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Always say "thanks for asking!" at the end of the answer. 
    {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
    # create vector database from data
    persist_directory = "./db/chroma"
    embeddings = OpenAIEmbeddings()
    #db = DocArrayInMemorySearch.from_documents(docs, embeddings)
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    # define retriever
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 3}, filter={"source":", ".join(files)})
    # create a chatbot chain. Memory is managed externally.
    qa = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model_name=llm_name, temperature=0), 
        chain_type="stuff", 
        retriever=retriever, 
        return_source_documents=True,
        # return_generated_question=True,
    )
    return qa 


class ChatDocBackend:
    """
        Class for handling LLM operations.
        STEP 1:
            - load newly uploaded document using PyPDFLoader and add loaded document in loaded_docs list
            - split loaded document using text_splitter, generate embeddings with openai and add it into
                chroma vector store.
            - 

        STEP 2:
            - user specify the document to chat with from storage and added to query using metadata_field_info
            - retrieve answer to a question using ConversationalRetrievalChain
            - store chat_history in memory
    """

    doc_storage_dir = StorageManager.docs_dir
    vectoredb_dir = "db/chroma"

    chat_history = []
    answer = ''
    # db_query  = ''
    db_response = []
    #new_docs = []
    loaded_docs = os.listdir(doc_storage_dir)

    def load_doc(self, new_doc):
        """
        ---- Called at successful document upload to storage ----
        this function load new pdf doc and store the embeddings in vectoredb.
        the new doc is added to loaded_docs list
        """
        loaded_docs = []
        if new_doc in loaded_docs:
            print("docs is loaded already")
            pass
        else:
            # load documents
            loader = PyPDFLoader(os.path.join(self.doc_storage_dir, new_doc))
            documents = loader.load()
            # split documents
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            splits = text_splitter.split_documents(documents)
            print(splits)
            # define embedding
            embeddings = OpenAIEmbeddings()
            # create vector database from data
            vectordb = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=self.vectoredb_dir
            )    
            print(f"{vectordb._collection.count()} embeddings stored successfully")
            loaded_docs = self.loaded_docs  # add new_doc to loaded list


    def unload_docs(self):
        """
            ---- Called at successful document delete from storage ---
            this function unload docs  in loaded_docs list and refresh vectoredb.
            selected docs is removed from loaded_docs list
        """
        
        # clean previous db
        if os.path.exists(self.vectoredb_dir):
            shutil.rmtree(self.vectoredb_dir)
            # print(f"Removed directory: {self.vectoredb_dir}")

        os.makedirs(os.path.join(os.getcwd(), "db"), exist_ok=True) # create db directory 
        # load document one by one
        # for fl in os.listdir(self.doc_storage_dir):
        #     print(fl)
        #     self.load_doc(fl)
        #     print(f"{str(fl)} loaded into vector store successfully")
            
    def run_query(self, question):
        """
            --- Function call at sending query ---
            - this function query the vectordb and resturn answers with references
        """
        embedding = OpenAIEmbeddings()
        vectordb = Chroma(persist_directory=self.vectoredb_dir, embedding_function=embedding)
        # print(vectordb._collection.count())

        docs = vectordb.similarity_search(question, k=3)
        # print(len(docs))
        llm = ChatOpenAI(model_name=llm_name, temperature=0)
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=vectordb.as_retriever(),
            #return_generated_question=True,
            return_source_documents=True,
        )
        result = qa_chain({"query": question})
        return result

    def message_handler(self, query, source_files):
        if not query:
            return 'No Chat Cistory'
        qa = load_db(source_files)
        result = qa({"question": query, "chat_history": self.chat_history})
        self.chat_history.extend([(query, result["answer"])])
        # self.db_query = result["generated_question"]
        self.db_response = result["source_documents"]
        self.answer = result['answer'] 
        return f"Chatbot: \n{str(self.answer)}", str(self.get_sources())
        # display_func(f"Chatbot: \n{str(self.answer)}", str(self.get_sources()), sent=False)

    # def message_handler(self, msg, display_func):
    #     result = self.run_query2(msg)
    #     # print(str(result["source_documents"]))
    #     display_func(f"Chatbot: \n{str(result['answer'])}", str(result["source_documents"]), sent=False)

    ''''def clr_history(self):
        self.loaded_docs = os.listdir(self.doc_storage_dir)
        self.chat_history = []
        self.answer = ''
        self.db_query  = ''
        self.db_response = []
    '''
        

    '''def get_chats(self):
        if not self.chat_history:
            return print("No History Yet")
        chat_list = []
        for exchange in self.chat_history:
            chat_list.append(str(exchange))
        return chat_list '''

    def get_sources(self):
        """
        Processes documents stored in `self.db_response` to extract unique metadata
        and returns a formatted string of page and source information.

        Returns:
            str: A string formatted with unique page and source information from documents.
        """
        if not self.db_response:
            return ""

        unique_metadata = {}
        for doc in self.db_response:
            metadata = doc.metadata
            source = os.path.basename(str(metadata['source']))
            page = metadata['page']
            metadata_key = f"{source}_{page}"

            if metadata_key not in unique_metadata:
                unique_metadata[metadata_key] = (page, source)

        response_parts = [f"Page: {info[0]}; Source: {info[1]}" for info in unique_metadata.values()]
        return ", ".join(response_parts)


    def get_lquest(self):
        if not self.db_query :
            return f"Last question to DB: no DB accesses so far"
        return f"DB query: {Str(self.db_query)}"

