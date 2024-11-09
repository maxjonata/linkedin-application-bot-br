import json

newlist = []
with open("data/answeredQuestions.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        line = json.loads(line)
        if "question" in line:
            newlist.append(line)
        else:
            lit = next(iter(line))
            newlist.append({
                "question": next(iter(line)),
                "answer": line[next(iter(line))]
            })

newliststring = "\n".join([json.dumps(jsonline) for jsonline in newlist])
with open("data/answeredQuestions.jsonl", "w", encoding="utf-8") as f:
    f.write(newliststring)