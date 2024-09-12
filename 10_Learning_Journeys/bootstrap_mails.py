from typing import Literal, Type, Union, Dict, Any, List
import re
import pathlib
from enum import Enum
import time
import json
import uuid

import yaml
from datasets import load_dataset
from pydantic import BaseModel, Field
import instructor

HERE = pathlib.Path(__file__).parent



class RateLimitedIterator:
    def __init__(self, iterable, max_iterations_per_minute):
        self._iterable = iter(iterable)
        self._max_iterations_per_minute = max_iterations_per_minute
        self._min_interval = 1.0 / (max_iterations_per_minute / 60.)
        self._last_yield_time = None

    def __iter__(self):
        return self

    def __next__(self):
        current_time = time.time()

        if self._last_yield_time is not None:
            elapsed_time = current_time - self._last_yield_time
            if elapsed_time < self._min_interval:
                time.sleep(self._min_interval - elapsed_time)

        self._last_yield_time = time.time()
        return next(self._iterable)


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Urgency(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


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
    import random
    with (HERE / 'draft-mail.yaml').open() as stream:
        draft_prompt = yaml.safe_load(stream)
    client = OpenAI()
    instructor_client = instructor.from_openai(client)

    with (HERE / 'service-categories.md').open() as stream:
        categories_description = stream.read()
        category_dict = extract_categories_to_dict(categories_description)

    with (HERE / 'company-scope.md').open() as stream:
        company_description = stream.read()

    personas = load_dataset("proj-persona/PersonaHub", 'persona', split='train')

    for _ in RateLimitedIterator(range(1000), 10):
        category = random.choice([*category_dict.keys()])
        kwargs = dict(
            id=str(uuid.uuid4()),
            persona=random.choice(personas)['persona'],
            category=category,
            category_description=category_dict[category],
            urgency=str(random.choice(list(Urgency))),
            sentiment=str(random.choice(list(Sentiment))),
        )

        mail = client.chat.completions.create(
            model='gpt-4o',
            messages=fill_prompt_template(draft_prompt, company=company_description,**kwargs),
            temperature=0.0,
        )
        kwargs["message"] = mail.choices[0].message.content
        with open(HERE / 'mails.jsonl', 'a') as stream:
            stream.write(json.dumps(kwargs)+'\n')
