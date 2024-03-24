import json
import utils
from fuzzywuzzy import process

class letFuzzyAnswer():
    def __init__(self):
        self.answeredQuestions = utils.getAnsweredQuestions()
        self.unansweredQuestions = utils.getErrorsListFromJson()
        self.answeredQuestionsLabels = [next(iter(question)) for question in self.answeredQuestions]
        for question in self.unansweredQuestions:
            closerAnswer = self.answer(question)
            if(closerAnswer == False):
                continue
            answer = {question["Label"]: closerAnswer[next(iter(closerAnswer))]}
            if closerAnswer and question["Options"] and closerAnswer[next(iter(closerAnswer))] in question["Options"]:
                continue
            else:
                with open("data/fuzzyAnsweredQuestions.json", "a", encoding="utf-8") as file:
                    file.write(json.dumps(answer, ensure_ascii=False) + "\n")

    def answer(self, question):
        question
        best_match, score = process.extractOne(question["Label"], self.answeredQuestionsLabels)
        if(score > 80):
            return next(item for item in self.answeredQuestions if next(iter(item)) == best_match)
        else:
            return False


if __name__ == "__main__":
    app = letFuzzyAnswer()