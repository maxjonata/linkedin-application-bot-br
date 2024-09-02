import utils
import json
from transformers import BertTokenizer, BertModel
import torch
from scipy.spatial.distance import cosine

class letBERTAnswers():
    def __init__(self):
        modelName = 'bert-base-uncased'
        self.tokenizer = BertTokenizer.from_pretrained(modelName)
        self.model = BertModel.from_pretrained(modelName)
        self.answeredQuestions = utils.getAnsweredQuestions()
        self.unansweredQuestions = utils.getErrorsListFromJson()
        self.answeredQuestionsLabels = list([next(iter(question)) for question in self.answeredQuestions])
        self.tokenizedAnsweredQuestionsLabels = self.tokenizer(self.answeredQuestionsLabels, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            self.modeledAnsweredQuestions = self.model(**self.tokenizedAnsweredQuestionsLabels)
        for question in self.unansweredQuestions:
            closerQuestion, closerQuestionCosine = self.answer(question)
            if not closerQuestion:
                continue
            with open("data/BERTAnswers.json", "a", encoding="utf-8") as file:
                closerAnswer = next(iter(self.answeredQuestions[self.answeredQuestionsLabels.index(closerQuestion)]))
                json.dump({question["Label"]: closerAnswer }, file, ensure_ascii=False)
                file.write("\n" + closerQuestion + ' / ' + str(closerQuestionCosine) + "\n")

    def answer(self, questionToAnswer):
        ## Receives a questionToAnswer dict that has a "Label" key with the question, loads the self.answeredQuestionsLabels with the Questions that were already answered and returns the answered question most similar to the queston to answer
        tokenizedQuestionToAnswer = self.tokenizer(questionToAnswer["Label"], padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            modelOutput = self.model(**tokenizedQuestionToAnswer)
        questionToAnswerEmbedding = modelOutput.last_hidden_state[0][0]
        closestAnswer = ""
        closestAnswerCosine = 2
        for i in range(len(self.tokenizedAnsweredQuestionsLabels["input_ids"])):
            answeredQuestionEmbedding = self.modeledAnsweredQuestions.last_hidden_state[i][0]
            cosineDistance = cosine(questionToAnswerEmbedding, answeredQuestionEmbedding)
            if cosineDistance < closestAnswerCosine:
                closestAnswerCosine = cosineDistance
                closestAnswer = self.answeredQuestionsLabels[i]
        if closestAnswerCosine > 0.008:
            return False, False
        return closestAnswer, closestAnswerCosine

        
if __name__ == "__main__":
    letBERTAnswers = letBERTAnswers()