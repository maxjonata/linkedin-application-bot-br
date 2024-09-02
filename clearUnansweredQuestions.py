import utils
import json

class clearUnansweredQuestions():
    def __init__(self):
        self.answeredQuestions = utils.getAnsweredQuestions()
        self.unansweredQuestions = utils.getErrorsListFromJson()
        files = ['RadioLabels', 'TextLabels', 'SelectLabels', 'CheckboxLabels']
        for fileName in files:
            newUnansweredList = []
            try:
                with open(f'data/unanswered{fileName}.json', 'r', encoding="utf-8") as json_file:
                    for line in json_file:
                        for question in self.unansweredQuestions:
                            if question["Label"] in line:
                                newUnansweredList.append(question)
                with open(f'data/unanswered{fileName}.json', 'w', encoding="utf-8") as json_file:
                    for question in newUnansweredList:
                        json.dump(question, json_file, ensure_ascii=False)
                        json_file.write('\n')
            except Exception as e:
                print(e)
                pass


if __name__ == "__main__":
    app = clearUnansweredQuestions()