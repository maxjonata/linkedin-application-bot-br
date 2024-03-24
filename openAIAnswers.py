import utils
import os
import json
from openai import OpenAI

class letOpenAIAnswer():
    def __init__(self):
        self.client = OpenAI()

    def fineTuneWithAnsweredQuestions(self):
        trainingData = []
        answers = utils.getAnsweredQuestions()
        for question in answers:
            prompt, completion = next(iter(question.items()))
            trainingData.append({
              "messages": [
                {"role": "system", "content": "Você está respondendo perguntas de uma aplicação de emprego no lugar de outra pessoa, com base nas perguntas e respostas que esta pessoa já respondeu"},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": completion}
              ]})
        with open ("data/trainingData.jsonl", "w", encoding="utf-8") as file:
            for data in trainingData:
                file.write(f"{json.dumps(data, ensure_ascii=False)}\n")

    def askAI(self):
        for question in self.unansweredQuestions:
            question["Answer"] = OpenAI.ask(question["Label"])
        return self.unansweredQuestions

    def formatAnswerListForGPT3(self):
        self.alreadyAnsweredQuestions = utils.getAnsweredQuestions()



if __name__ == "__main__":
    ai = letAIAnswerUnansweredQuestions()
    ai.fineTuneWithAnsweredQuestions()
    a=None