import json
import logging
logging.basicConfig(level=logging.DEBUG)
import spacy
from spacy.lang.en import English
import requests
from huggingface_hub import HfApi


from pyattck import Attck

from tqdm import tqdm

def gen_enterprise_attck_alpaca():
    """
    Create a training dataset in the ALPACA format
    :return:
    """

    logging.debug("Loading TRAM....")
    # everything is the latest version
    r = requests.get("https://raw.githubusercontent.com/center-for-threat-informed-defense/tram/main/data/training/attack_may_2023_merged_bootstrap_data2.json")

    data = r.json()
    sentences = data['sentences']
    logging.debug("Done loading!")

    INSTRUCTION = "List the MITRE techniques contained in the text."

    template = {"instruction": INSTRUCTION, "input": None, "output": None,"text":None}

    alpaca_text = "Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request. ### Instruction: {0} ### Input: {1} ### Response: {2}."
    samples = []

    logging.debug("Generating training set via sentence split")

    with tqdm(total=len(sentences)) as pbar:
        for sentence in sentences:
            all_ids = []
            for mapping in sentence['mappings']:
                all_ids.append(mapping["attack_id"])

            template['input'] =  sentence['text']
            template['output'] = ",".join(all_ids)
            template['text'] = alpaca_text.format(INSTRUCTION,sentence['text'],",".join(all_ids))

            samples.append(template.copy())

            pbar.update(1)

    with open("./modal/enterprise_tram_attack.jsonl","w") as file:
        for sample in samples:
            file.write(json.dumps(sample)+"\n")

    #push to hugging face
    api = HfApi()
    api.upload_file(
        path_or_fileobj="./modal/enterprise_tram_attack.jsonl",
        path_in_repo="enterprise_tram_attack.jsonl",
        repo_id="priamai/cti-llm-datasets",
        repo_type="dataset",
    )

    logging.debug("Saved as JSONL")

from huggingface_hub import create_repo
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-create_repo", default=False, action="store_true")
    parser.add_argument("-test_spacy", default=False,action="store_true")
    parser.add_argument("-gen_training", default=True, action="store_true")

    args = parser.parse_args()

    if args.create_repo:
        create_repo("priamai/cti-llm-datasets", repo_type="dataset",private=False)

    if args.gen_training:
        gen_enterprise_attck_alpaca()


