import json

with open('data.json') as f:
    data = json.load(f)

for quiz in data:
    warn = 0
    error = 0
    quiz_data = quiz["quiz_data"]
    print("Checking quiz: " + quiz["quiz_name"])
    for index, question in enumerate(quiz_data.keys()):
        if len(question) > 300:
            print("Warn: Exceeding length of 300 for question {}".format(index + 1))
            warn += 1
        question_dict = quiz_data[question]
        try:
            answer = question_dict["answer"]
        except KeyError:
            print("Error: Missing field \"answer\" for question " + index + 1)
            error += 1

        try:
            options = question_dict["options"]
            for i, v in enumerate(options):
                if len(v) > 100:
                    print("Warn: Exceeding length of 100 for question {}, option: {}".format(
                        index + 1, i + 1))
                    warn += 1
        except KeyError:
            print("Error: Missing field \"options\" for question " + index + 1)
            error += 1

    print("{} error, {} warn".format(error, warn))
