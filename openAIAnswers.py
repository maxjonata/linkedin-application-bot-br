import utils
import os
import json
from openai import OpenAI

class letOpenAIAnswer():
    def __init__(self):
        self.client = OpenAI()

    def fineTuneWithAnsweredQuestions(self):
        trainingData = []
        list_of_questions_as_messages = []
        answers = utils.getAnsweredQuestions()
        i = 0
        for question in answers:
            i+=1
            if i == 10:
                break
            prompt, completion = next(iter(question.items()))
            list_of_questions_as_messages.append({"role": "user", "content": f"Questão: {prompt} | Resposta: {completion}"})
        questions = utils.getErrorsListFromJson()
        list_of_questions_to_ask = []
        i = 0
        for question in questions:
            i+=1
            if i == 10:
                break
            prompt = question["Label"]
            list_of_questions_to_ask.append({"role": "user", "content": f"Pergunta: {prompt}"})

        trainingData.append({"role": "system", "content": "Você está respondendo perguntas de uma aplicação de emprego no lugar de outra pessoa, com base nas perguntas e respostas que esta pessoa já respondeu. As perguntas já respondidas serão enviadas como Questão | Resposta e as perguntas para as quais deve responder será enviada como Pergunta:*pergunta aqui*"})
        trainingData.extend([*list_of_questions_as_messages, *list_of_questions_to_ask])
        
        for line in trainingData:
            with open("trainingData.txt", "a") as file:
                file.write(f"{line}\n")
        teste = self.client.chat.completions.create(model="gpt-3.5-turbo", messages=trainingData)
        a = None

    def askAI(self):
        for question in self.unansweredQuestions:
            question["Answer"] = OpenAI.ask(question["Label"])
        return self.unansweredQuestions

    def formatAnswerListForGPT3(self):
        self.alreadyAnsweredQuestions = utils.getAnsweredQuestions()



if __name__ == "__main__":
    ai = letOpenAIAnswer()
    ai.fineTuneWithAnsweredQuestions()
    a=None