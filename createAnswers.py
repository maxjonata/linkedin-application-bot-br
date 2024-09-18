import json
import os
import shutil
import time  # Para simulação de tempo, se necessário
from typing import TypedDict, cast

import torch
from torch.nn.utils import clip_grad_norm_
from tqdm import tqdm
from transformers import GPT2LMHeadModel, GPT2Tokenizer

from config_local import Presentation

_GlobalModel = "gpt2"
_GlobalTokenLength = 512
torch.set_num_threads(2) # Do not use more or equal to core count as it can cause CPU crash

class QATrainingData(TypedDict):
    question: str
    answer: str

class CreateAnswers:
    def __init__(self, presentation):
        self.presentation = presentation
        self.answeredQuestions: list[QATrainingData] = []

        self.Auxiliaries.clear_transformers_cache()
        self.loadModel()

    def loadAnsweredQuestions(self):
        with open("data/answeredQuestions.json", "r", encoding="utf-8") as file:
            self.answeredQuestions = json.load(file)

    def saveAnswers(self):
        with open("data/answeredQuestions.json", "w", encoding="utf-8") as file:
            json.dump(self.answeredQuestions, file)

    def fineTuneModel(self, train_data: list[QATrainingData], epochs=1, learning_rate=1e-5, max_grad_norm=0.5, batch_size=1):
        if not train_data:
            return "There is no training data"
        
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate) # type:ignore
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.model.config.eos_token_id

        questionToken, answerToken = "<QUESTION>", "<ANSWER>"
        special_tokens = {"additional_special_tokens": [questionToken, answerToken]}
        self.tokenizer.add_special_tokens(special_tokens) # type: ignore
        self.model.resize_token_embeddings(len(self.tokenizer))

        for epoch in range(epochs):
            total_loss = 0
            with tqdm(total=len(train_data), desc=f'Epoch {epoch + 1}', unit='batch') as pbar:
                for i in range(0, len(train_data), batch_size):
                    batch = train_data[i:i + batch_size]
                    tokenSize = _GlobalTokenLength

                    input_texts = [f"{questionToken}{data['question']}{answerToken}{data['answer']}{self.tokenizer.eos_token}" for data in batch]

                    input_ = self.tokenizer(input_texts, return_tensors="pt", truncation=True, padding=True, max_length=tokenSize)
                    input_ids = input_.input_ids
                    attention_mask = input_.attention_mask
                    
                    labels = input_ids.clone()
                    
                    # Encontrar a posição do token <RESPOSTA> e definir as labels
                    for j, input_seq in enumerate(input_ids):
                        try:
                            response_start = (input_seq == self.tokenizer.additional_special_tokens_ids[1]).nonzero(as_tuple=True)[0]
                            labels[j, :response_start] = -100  # Ignorar a perda para a parte da pergunta
                        except Exception as e:
                          print(f"Error at tensor {j}: {e}")


                    self.tokenizer.encode([data["answer"] for data in batch], return_tensors="pt", truncation=True, padding="max_length", max_length=tokenSize)  

                    outputs = self.model(input_ids, labels=labels, attention_mask=attention_mask)
                    loss = outputs[0] if isinstance(outputs, tuple) else outputs.loss

                    loss.backward()
                    clip_grad_norm_(self.model.parameters(), max_grad_norm)

                    optimizer.step()
                    optimizer.zero_grad()
            
                    total_loss += loss.item()
                    pbar.update(len(batch))
            print(f"Epoch {epoch + 1}: Mean Loss: {total_loss / len(train_data)}")
                    
        model_path = "data/trainedModel/"
        self.model.save_pretrained(model_path)
        self.tokenizer.save_pretrained(model_path)
        print(f"Model saved successfully at: {model_path}")
        return "Model trained successfully"

    def loadModel(self):
        if not os.path.exists("data/trainedModel/"):
            model_path = "gpt2"
        else:
            model_path = "data/trainedModel/"
        self.model = cast(GPT2LMHeadModel, GPT2LMHeadModel.from_pretrained(model_path))
        self.tokenizer = cast(GPT2Tokenizer, GPT2Tokenizer.from_pretrained(model_path))  

    class Auxiliaries:
        @staticmethod
        def getAnsweredQuestions() -> list[QATrainingData]:
            questions: list[QATrainingData] = []
            with open("data/answeredQuestions.json", "r", encoding="utf-8") as file:
                for question in json.load(file):
                    questions.append({
                        "question": next(iter(question)),
                        "answer": question[next(iter(question))]
                    })
            return questions
        @staticmethod
        def clear_transformers_cache():
            # Obter o diretório home do usuário
            home = os.path.expanduser("~")
            
            # Possíveis localizações do cache
            cache_dirs = [
                os.path.join(home, '.cache', 'huggingface'),
                os.path.join(home, '.cache', 'torch'),
            ]

            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    print(f"Cache found at: {cache_dir}")
                    try:
                        shutil.rmtree(cache_dir)
                        print(f"Cache removed successfully: {cache_dir}")
                    except Exception as e:
                        print(f"Error removing cache {cache_dir}: {e}")
                else:
                    print(f"Cache directory not found: {cache_dir}")

            print("Cache cleaning completed.")

if __name__ == "__main__":
    createAnswers = CreateAnswers(Presentation)
