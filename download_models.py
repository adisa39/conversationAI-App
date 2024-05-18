from transformers import GPT2LMHeadModel, GPT2Tokenizer
from sentence_transformers import SentenceTransformer

def download_and_save_models():
    # Download GPT-2 model and tokenizer
    gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")

    # Save the models locally
    gpt2_tokenizer.save_pretrained('./models/gpt2')
    gpt2_model.save_pretrained('./models/gpt2')

    # Download Sentence-BERT model
    bert_model = SentenceTransformer('bert-base-nli-mean-tokens')
    bert_model.save('./models/bert-base-nli-mean-tokens')

if __name__ == "__main__":
    download_and_save_models()
