from sympy import ask
import config_local
from openai import OpenAI
import utils
import json

class letOpenAIAnswer():
    def __init__(self):
        self.client = OpenAI(
            api_key=config_local.openai_APIKEY
        )
        self.messages = [{"role": "system", "content": f"You are a concise candidate for a job at a Tech Company. Answer everything as truthfully as possible based on the provided job experience description. If the description does not explicitly mention something. Use a respectful tone suitable for a professional interview. If asked for a salary, respond with just a number unless the question specifies a time period. If the user asks specifically 'WDYK?', summarize all relevant information you could not address during the conversation due to gaps in the provided experience the most concize as possible not following other directives on how to talk. Format all answers to match the style and language of the question, keeping them concise and direct. Use only one line if possible. If a question cannot reasonably be answered even with inference, respond with 'NOT SURE'. Your job experience is described as following: '{config_local.openai_JobExperienceDescription}'"}]
        self.unanswered_questions = []
        self.answered_questions = []

    def getChatAnswer(self, user_message):
        self.messages.append({"role": "user", "content": user_message})
        chat = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages
        )
        answer = chat.choices[0].message.content
        self.messages.append({"role": "assistant", "content": answer})
        return answer

    def askQuestion(self, question, options=None):
        if options:
            question += " Options: " + ", ".join(options)
        answer = self.getChatAnswer(question)
        if "NOT SURE" in answer:
            self.unanswered_questions.append({"question": question, "answer": answer})
        else:
            self.answered_questions.append({"question": question, "answer": answer})
        return answer
  
    def answerUnansweredQuestionsToFile(self):
        for question in utils.getErrorsListFromJson():
            self.askQuestion(question["Label"], question.get("Options"))
        with open("answeredOpenAIQuestionsTest.jsonl", "w") as file:
            file.write(json.dumps(self.answered_questions) + "\n")

    def getUnansweredQuestions(self):
        return self.unanswered_questions
    
    def getAnsweredQuestions(self):
        return self.answered_questions

if __name__ == "__main__":
    ai = letOpenAIAnswer()
    # Example usage:
    # print(ai.askQuestion("What courses have you taken?"))
    # print(ai.askQuestion("What is your work experience?"))
    # print(ai.askQuestion("How many years of farming experience do you have?"))
    # print(ai.askQuestion("How well can you drive a car?"))
    # print(ai.askQuestion("Would you be able to relocate for the job?"))
    # print(ai.askQuestion("Do you have experience with software development? Options: Yes, No, Not sure"))
    # print(ai.askQuestion("Do you have experience with Kubernetes? Options: Yes, No, Not sure, Experience with Docker"))
    # print(ai.askQuestion("How well can you speak English?"))
    # print(ai.getUnansweredQuestions())
    # print(ai.getAnsweredQuestions())
    # print(ai.askQuestion("WDYK?"))
    ai.answerUnansweredQuestionsToFile()