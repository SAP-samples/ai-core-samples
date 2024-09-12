from typing import Dict
import re
import pathlib
import sys
import json

import yaml

from gen_ai_hub.proxy.native.openai import OpenAI

HERE = pathlib.Path(__file__).parent
PRINT_FORMATTED_PROMPT = True
MESSAGE_IDX = int(sys.argv[1]) if len(sys.argv) > 1 else 0

with (HERE / 'example-prompts.yaml').open() as stream:
    prompts = yaml.safe_load(stream)

with (HERE / 'mails-v2.json').open() as stream:
    mails = [json.loads(line) for line in stream if line.strip()]

with (HERE / 'service-categories.md').open() as stream:
    categories = stream.read()

mail = mails[MESSAGE_IDX]


client = OpenAI()

def send_request(prompt, message,**kwargs) -> str:
    formatted_prompt = prompt.format(message=message, **kwargs)
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{"role": "user", "content": formatted_prompt}],
        temperature=0.0,
    ).choices[0].message.content
    print(f"<-- PROMPT --->\n{formatted_prompt if PRINT_FORMATTED_PROMPT else prompt}\n<--- RESPONSE --->\n{response}")
    return response


key = "01_basic"
print(f"###\n\t{key}\n###")
response = send_request(prompts[key], mail["message"])

key = "02_sentiment_urgency_choices"
print(f"###\n\t{key}\n###")
response = send_request(prompts[key], mail["message"])

key = "03_sentiment_urgency_choices_as_json"
print(f"###\n\t{key}\n###")
response = send_request(prompts[key], mail["message"])

key = "04_sentiment_urgency_choices_as_json_no_wrapping"
print(f"###\n\t{key}\n###")
response = send_request(prompts[key], mail["message"])

key = "05_assign_category"
print(f"###\n\t{key}\n###")
response = send_request(prompts[key], mail["message"])


key = "06_assign_category_with_description"
print(f"###\n\t{key}\n###")
response = send_request(prompts[key], mail["message"], categories=categories)

key = "07_assign_category_with_description_json"
print(f"###\n\t{key}\n###")


def extract_categories_to_dict(text: str) -> dict:
    # Split the text into sections based on the numbered list
    sections = re.split(r'\n(?=\d+\.\s+\*\*)', text)
    categories_dict = {}

    for section in sections:
        # Extract the header and the content
        header_match = re.search(r'\*\*(.*?)\*\*', section)
        if header_match:
            header = header_match.group(1).lower().replace(' ', '_')
            # Remove the header and leading number from the section
            content = [l.lstrip("1234567890. ") for l in section.splitlines()]
            categories_dict[header] = '\n'.join(content)
    return categories_dict

categories_dict = extract_categories_to_dict(categories)
response = send_request(prompts[key], mail["message"], categories=categories, categories_list=', '.join([*categories_dict.keys()]))


key = "08_complete"
print(f"###\n\t{key}\n###")
response = send_request(prompts[key], mail["message"], categories=categories, categories_list=', '.join([*categories_dict.keys()]))


### Evaluation

def evaluation(mail: Dict[str, str], response: str):
    is_valid_json = False
    is_correct_category = False
    is_correct_sentiment = False
    is_correct_urgency = False

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        is_valid_json = False
    else:
        is_valid_json = True
        is_correct_category = result["category"] == mail["ground_truth"]["category"]
        is_correct_sentiment = result["sentiment"] == mail["ground_truth"]["sentiment"]
        is_correct_urgency = result["urgency"] == mail["ground_truth"]["urgency"]

    print(f"<-- Evaluation -->\n\t{is_valid_json=}\n\t{is_correct_category=}\n\t{is_correct_sentiment=}\n\t{is_correct_urgency=}")
    return is_valid_json, is_correct_category, is_correct_sentiment, is_correct_urgency


        print(f"\n\t{is_valid_json=}
        print(f"\n\t{is_correct_category=}")
        print(f"\n\t{is_correct_sentiment=}")
        print(f"\n\t{is_correct_urgency=}")")
print(evaluation(mail, response))


n_valid_json = 0
n_correct_sentiment = 0
n_correct_category = 0
n_correct_urgency = 0
for main in mails:
    is_valid_json, is_correct_category, is_correct_sentiment, is_correct_urgency = evaluation(mail, f_8)
    n_valid_json += is_valid_json
    n_correct_sentiment += is_correct_sentiment
    n_correct_category += is_correct_category
    n_correct_urgency += is_correct_urgency
