import json

list = json.load(open("data/answeredQuestions.json", "r", encoding="utf-8"))
newlist = []
for question in list:
    newlist.append({
        "question": next(iter(question)),
        "answer": question[next(iter(question))]
    })

json.dump(newlist, open("data/answeredQuestions.json", "w", encoding="utf-8"), sort_keys=True, indent=2, separators=(',', ': '))