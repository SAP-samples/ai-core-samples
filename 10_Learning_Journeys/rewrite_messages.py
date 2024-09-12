from typing import Literal, Type, Union, Dict, Any, List, Callable
import re
from enum import Enum
import pathlib
import instructor
from datasets import load_dataset
from pydantic import BaseModel, create_model
import yaml
import json
from tqdm.auto import tqdm

HERE = pathlib.Path(__file__).parent



class MatchLevel(str, Enum):
    VERY_LOW = 'very low'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    VERY_HIGH = 'very high'


class Match(BaseModel):
    persona: Literal['very low', 'low', 'medium', 'high', 'very high']
    category: Literal['very low', 'low', 'medium', 'high', 'very high']
    urgency: Literal['very low', 'low', 'medium', 'high', 'very high']
    sentiment: Literal['very low', 'low', 'medium', 'high', 'very high']

    @property
    def score(self):
        f_str2int = lambda s: {'very low': 1, 'low': 2, 'medium': 3, 'high': 4, 'very high': 5}[s]
        scores = [f_str2int(getattr(self, field)) for field in self.model_fields.keys()]
        return sum(scores) / len(scores)


class Urgency(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

def fill_prompt_template(prompt: Union[str, List[Any], Dict[Any, Any]], **kwargs) -> Union[str, List[Any], Dict[Any, Any]]:
    if isinstance(prompt, str):
        return prompt.format(**kwargs)
    elif isinstance(prompt, list):
        return [fill_prompt_template(item, **kwargs) for item in prompt]
    elif isinstance(prompt, dict):
        return {key: fill_prompt_template(value, **kwargs) for key, value in prompt.items()}
    else:
        return prompt


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


if __name__ == '__main__':
    from gen_ai_hub.proxy.native.openai import OpenAI

    MODEL = 'gpt-4o'

    with (HERE / 'rewrite-messages.yaml').open() as stream:
        prompts = yaml.safe_load(stream)

    with (HERE / 'service-categories.md').open() as stream:
        categories_description = stream.read()
        category_dict = extract_categories_to_dict(categories_description)

    with (HERE / 'urgency-description.md').open() as stream:
        urgency_description = stream.read()
        urgency_dict = extract_categories_to_dict(urgency_description)

    with (HERE / 'company-scope.md').open() as stream:
        company_description = stream.read()
        category_dict = extract_categories_to_dict(categories_description)
        categories = list(category_dict.keys())

    fields = {cat: (bool, ...) for cat in categories}
    fields["urgency"] = (Urgency, ...)
    MultiLabelResponse = create_model("AssignedCategories", **fields)

    client = OpenAI()
    instructor_client = instructor.from_openai(client)


    output_file = HERE / 'mails-v4.jsonl'
    if output_file.exists():
        known_ids = set([entry["id"] for entry in load_dataset("json", data_files=[str(output_file)], split='train')])
    else:
        known_ids = set()

    dataset = load_dataset("json", data_files=["mails-v2.jsonl"], split='train')

    kwargs = {
        "company": company_description,
    }

    new_messages = []

    def render_categories(info_dict: Dict[str, str], categories: List[str]) -> str:
        categories = [f"## `{cat}`: {info_dict[cat]}" for cat in categories]
        return '\n'.join(categories)

    for entry in tqdm(dataset):
        if entry["id"] in known_ids:
            continue
        if "sentiment" in entry:
            sentiment = entry["sentiment"].split('.')[-1].lower()
        elif "sentiment" in entry["ground_truth"]:
            sentiment = entry["ground_truth"]["sentiment"].split('.')[-1].lower()

        formatted_prompt = fill_prompt_template(
            prompts["assign-labels"],
            message=entry["message"],
            urgency_description=render_categories(urgency_dict, urgency_dict.keys()),
            categories=render_categories(category_dict, category_dict.keys())
        )
        classification = instructor_client.chat.completions.create(
            model='gpt-4o',
            messages=formatted_prompt,
            response_model=MultiLabelResponse,
            temperature=0.0,
        ).model_dump()
        print(f'{classification=}')
        urgency_assigned = classification.pop("urgency").value.lower()
        categories_assigned = [k for k, v in classification.items() if v]
        categories_avoided = list(set(categories) - set(categories_assigned))
        urgency_avoided = list(set([*urgency_dict.keys()]) - set([urgency_assigned]))

        inputs ={
                "categories_avoided_full": render_categories(category_dict, categories_avoided),
                "categories_avoided": ', '.join(categories_avoided),
                "categories_assigned_full": render_categories(category_dict, categories_assigned),
                "categories_assigned": ', '.join(categories_assigned),
                "urgency_avoided_full": render_categories(urgency_dict, urgency_avoided),
                "urgency_avoided": ', '.join(urgency_avoided),
                "urgency_assigned_full": render_categories(urgency_dict, [urgency_assigned]),
                "urgency_assigned": urgency_assigned,
                "sentiment": sentiment,
                "persona": entry["persona"],
                "message": entry["message"],
                **kwargs,
                #**entry
            }
        mail = client.chat.completions.create(
            model='gpt-4o',
            messages=fill_prompt_template(prompts["rewrite-message"], **inputs),
            temperature=0.0,
        )
        new_message = mail.choices[0].message.content


        rating = instructor_client.chat.completions.create(
            model='gpt-4',
            messages=fill_prompt_template(prompts["quality_rating"], **inputs),
            response_model=Match,
            temperature=0.0,
        )
        revised_entry = {
            "id": entry["id"],
            "persona": entry["persona"],
            "ground_truth": {
                "categories": categories_assigned,
                "sentiment": sentiment,
                "urgency": urgency_assigned,
            },
            "quality_score": rating.score,
            "generation_quality": rating.model_dump(),
        }
        if "<ACCEPT>" in new_message:
            revised_entry["message"] = entry["message"]
            revised_entry["original_message"] = None
        else:
            revised_entry["message"] = new_message
            revised_entry["original_message"] = entry["message"]
        with output_file.open('a') as stream:
            stream.write(json.dumps(revised_entry)+'\n')
