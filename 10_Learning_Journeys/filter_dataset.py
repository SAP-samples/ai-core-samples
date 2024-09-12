import json
import random

from datasets import load_dataset

import yaml


def str_presenter(dumper, data):
    if '\n' in data:  # Check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

dataset = load_dataset("json", data_files=["mails-v4.jsonl"], split='train')
sorted_dataset = dataset.sort("quality_score", reverse=True)
for offset, category in [(0, "easiest"), (200, "easy"), (400, "medium"), (600, "hard"), (800, "hardest")]:
    lines = []
    cropped_dataset = sorted_dataset.select([offset+i for i in range(200)])


    l = []
    for entry in cropped_dataset:
        l.append({
            "id": entry["id"],
            "message": entry["message"],
            "ground_truth": entry["ground_truth"]
        })
    random.seed(42)
    random.shuffle(l)
    with open(f"filtered_mails-{category}.yaml", "w") as f:
        yaml.dump(l, f, allow_unicode=True)
    with open(f"filtered_mails-{category}.jsonl", "w") as f:
        f.write("\n".join([json.dumps(m) for m in l]))
