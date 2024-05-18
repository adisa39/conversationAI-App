from transformers import GPT2LMHeadModel, GPT2Tokenizer
from sentence_transformers import SentenceTransformer

# Load GPT-2 model and tokenizer from local path
gpt2_tokenizer = GPT2Tokenizer.from_pretrained('./models/gpt2')
gpt2_model = GPT2LMHeadModel.from_pretrained('./models/gpt2')

# Load Sentence-BERT model from local path
bert_model = SentenceTransformer('./models/bert-base-nli-mean-tokens')
