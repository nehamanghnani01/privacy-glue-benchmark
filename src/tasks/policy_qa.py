#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from glob import glob
import datasets
import json
import os


def load_policy_qa(directory: str) -> datasets.DatasetDict:
    # define DatasetDict for data storage
    combined = datasets.DatasetDict()

    # loop over JSON files
    for json_file in glob(os.path.join(directory, "*.json")):
        # infer split from filename
        filename = os.path.basename(json_file)
        split = "train" if filename.startswith("train") else (
            "validation" if filename.startswith("dev") else "test")

        # define temporarily dictionary
        temp_dict = {
            "id": [],
            "title": [],
            "context": [],
            "question": [],
            "question_type": [],
            "answers": []
        }

        # read JSON file
        with open(json_file, "r") as input_file_stream:
            dataset = json.load(input_file_stream)

        # loop over data and save to dictionray
        for article in dataset["data"]:
            title = article["title"]
            for paragraph in article["paragraphs"]:
                context = paragraph["context"]
                answers = {}
                for qa in paragraph["qas"]:
                    question = qa["question"]
                    question_type = qa["type"]
                    idx = qa["id"]
                    answers["text"] = [
                        answer["text"] for answer in qa["answers"]
                    ]
                    answers["answer_start"] = [
                        answer["answer_start"] for answer in qa["answers"]
                    ]
                    temp_dict["id"].append(idx)
                    temp_dict["title"].append(title)
                    temp_dict["context"].append(context)
                    temp_dict["question"].append(question)
                    temp_dict["question_type"].append(question_type)
                    temp_dict["answers"].append(answers)

        # convert temp_dict to Dataset
        combined[split] = datasets.Dataset.from_dict(temp_dict)

    # split question_type column
    combined = combined.map(
        lambda example:
        {"question_type": example["question_type"].split("|||")})

    # return final DatasetDict
    return combined
