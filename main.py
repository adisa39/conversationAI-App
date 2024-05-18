import os
import time
import torch
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from docx import Document
import PyPDF2
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from sentence_transformers import SentenceTransformer, util
import faiss
import numpy as np

KV = '''
BoxLayout:
    orientation: 'vertical'
    padding: dp(10)
    spacing: dp(10)

    MDRaisedButton:
        text: "Upload Document"
        on_release: app.file_manager_open()
        pos_hint: {"center_x": .5}

    MDTextField:
        id: query_input
        hint_text: "Ask your question here"
        mode: "rectangle"
        size_hint_x: None
        width: dp(300)
        pos_hint: {"center_x": .5}

    MDRaisedButton:
        text: "Chat with Document"
        on_release: app.chat_with_document()
        pos_hint: {"center_x": .5}

    MDLabel:
        id: response_label
        text: ""
        halign: "center"
'''

class DocumentChatApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        self.gpt2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.gpt2_model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.bert_model = SentenceTransformer('bert-base-nli-mean-tokens')

        self.docs = {}
        self.embeddings = []

        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=False
        )

        # Initialize FAISS index
        self.faiss_index = faiss.IndexFlatL2(self.bert_model.get_sentence_embedding_dimension())
        self.doc_names = []

        return Builder.load_string(KV)

    def file_manager_open(self):
        self.file_manager.show(os.path.expanduser("~"))

    def select_path(self, path):
        try:
            self.load_document(path)
        except Exception as e:
            self.root.ids.response_label.text = f"Error loading document: {str(e)}"
        self.file_manager.close()

    def exit_manager(self, *args):
        self.file_manager.close()

    def load_document(self, filepath):
        for _ in range(5):  # Retry up to 5 times
            try:
                ext = os.path.splitext(filepath)[1].lower()
                text = ""
                if ext == ".pdf":
                    text = self.extract_text_from_pdf(filepath)
                elif ext == ".docx":
                    text = self.extract_text_from_docx(filepath)

                if text:
                    self.docs[os.path.basename(filepath)] = text
                    embedding = self.bert_model.encode(text, convert_to_tensor=True).cpu().numpy()
                    if len(embedding.shape) == 1:
                        embedding = embedding.reshape(1, -1)  # Ensure embedding is 2D
                    self.faiss_index.add(embedding)
                    self.doc_names.append(os.path.basename(filepath))
                    self.root.ids.response_label.text = f"Loaded {os.path.basename(filepath)}"
                return
            except Exception as e:
                time.sleep(1)  # Wait for 1 second before retrying
                self.root.ids.response_label.text = f"Retrying due to error: {str(e)}"
        self.root.ids.response_label.text = f"Failed to load document after multiple attempts."

    def extract_text_from_pdf(self, filepath):
        text = ""
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
        return text

    def extract_text_from_docx(self, filepath):
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])

    def generate_response(self, prompt):
        max_input_length = 1024  # Set a maximum input length for GPT-2
        inputs = self.gpt2_tokenizer.encode(prompt, return_tensors='pt', truncation=True, max_length=max_input_length)
        attention_mask = torch.ones(inputs.shape, dtype=torch.long)  # Create attention mask
        outputs = self.gpt2_model.generate(inputs, attention_mask=attention_mask, max_new_tokens=100, num_return_sequences=1, pad_token_id=self.gpt2_tokenizer.eos_token_id)
        return self.gpt2_tokenizer.decode(outputs[0], skip_special_tokens=True)

    def chat_with_document(self):
        query = self.root.ids.query_input.text
        if not query:
            self.root.ids.response_label.text = "Please enter a question."
            return

        query_embedding = self.bert_model.encode(query, convert_to_tensor=True).cpu().numpy()
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)  # Ensure query_embedding is 2D
        D, I = self.faiss_index.search(query_embedding, k=1)  # Search for the nearest neighbor

        responses = []
        for idx in I[0]:
            if idx != -1:  # Check if a valid index is found
                doc_name = self.doc_names[idx]
                doc_text = self.docs[doc_name]
                truncated_doc_text = doc_text[:1000]  # Truncate document text to fit within token limit
                generated_text = self.generate_response(f"Context: {truncated_doc_text}\n\nQuestion: {query}\nAnswer: ")
                response = f"[Source: {doc_name}]\n{generated_text}"
                responses.append(response)

        if responses:
            self.root.ids.response_label.text = "\n\n".join(responses)
        else:
            self.root.ids.response_label.text = "No relevant document found."

if __name__ == '__main__':
    DocumentChatApp().run()
