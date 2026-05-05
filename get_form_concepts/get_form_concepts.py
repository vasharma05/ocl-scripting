import os
import json
from resources import form_path, forms


def extract_form_concepts(form_data):
    concepts = set()
    pages = form_data["pages"]
    for page in pages:
        for section in page["sections"]:
            for questions in section["questions"]:
                questionOptions = questions["questionOptions"]
                if "concept" in questionOptions:
                    concepts.add(questionOptions["concept"])
                if "answers" in questionOptions:
                    for answer in questionOptions["answers"]:
                        if "concept" in answer:
                            concepts.add(answer["concept"])
    return concepts


def extract_form_labels(form_data):
    labels = set()
    pages = form_data["pages"]
    for page in pages:
        labels.add(page["label"])
        for section in page["sections"]:
            labels.add(section["label"])
            for question in section["questions"]:
                labels.add(question.get("label", ""))
                questionOptions = question["questionOptions"]
                if "answers" in questionOptions:
                    for answer in questionOptions["answers"]:
                        labels.add(answer["label"])
                if "buttonLabel" in questionOptions:
                    labels.add(questionOptions["buttonLabel"])
                if "questionInfo" in question:
                    labels.add(question["questionInfo"])
                if "value" in question:
                    if type(question["value"]) == list:
                        for value in question["value"]:
                            labels.add(value)
                    else:
                        labels.add(question["value"])
    return labels


all_concepts = set()
form_concepts_map = {}

for form in forms:
    path = os.path.join(form_path, form)
    with open(path, "r") as f:
        form_data = json.load(f)
    concepts = extract_form_concepts(form_data)
    labels = extract_form_labels(form_data)
    all_concepts.update(concepts)
    form_concepts_map[form] = {
        "concepts": list(concepts),
        "labels": {label: label for label in sorted(labels)},
    }

with open("get_form_concepts/results.json", "w") as f:
    results = {
        "form_concepts_map": form_concepts_map,
        "all_concepts": list(all_concepts),
    }
    json.dump(results, f, indent=4)
