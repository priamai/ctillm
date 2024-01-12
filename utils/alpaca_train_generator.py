import json
import logging
logging.basicConfig(level=logging.DEBUG)
import spacy
from spacy.lang.en import English

from huggingface_hub import HfApi


from pyattck import Attck

def test_sentence()->list[str]:
    nlp_web_en = spacy.load('en_core_web_sm')
    nlp_web_en.add_pipe("sentencizer")
    check_len = 4
    test_paragraph = """
Adversaries may execute active reconnaissance scans to gather information that can be used during targeting. Active scans are those where the adversary probes victim infrastructure via network traffic, as opposed to other forms of reconnaissance that do not involve direct interaction.
Adversaries may perform different forms of active scanning depending on what information they seek to gather. These scans can also be performed in various ways, including using native features of network protocols such as ICMP.[1][2] Information from these scans may reveal opportunities for other forms of reconnaissance (ex: Search Open Websites/Domains or Search Open Technical Databases), establishing operational resources (ex: Develop Capabilities or Obtain Capabilities), and/or initial access (ex: External Remote Services or Exploit Public-Facing Application).
    """
    sent_spans = list(nlp_web_en(test_paragraph).sents)
    for sent in sent_spans:
        text_sent = sent.text.strip()

    assert len(sent_spans)==check_len
    print("There are %d" % len(sent_spans))

from tqdm import tqdm

def gen_enterprise_attck_alpaca():
    """
    Create a training dataset in the ALPACA format
    :return:
    """
    nlp_web_en = spacy.load('en_core_web_sm')
    nlp_web_en.add_pipe("sentencizer")
    logging.debug("Loading ATTCK....")
    # everything is the latest version
    attck = Attck(
        nested_techniques=False,
        use_config=True,
        save_config=True,
        config_file_path='./pyattck/config.yml',
        data_path='./pyattck/data',
        enterprise_attck_json="https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json",
        #pre_attck_json="https://raw.githubusercontent.com/mitre/cti/master/pre-attack/pre-attack.json",
        #mobile_attck_json="https://raw.githubusercontent.com/mitre/cti/master/mobile-attack/mobile-attack.json",
        #ics_attck_json="https://raw.githubusercontent.com/mitre/cti/master/ics-attack/ics-attack.json",
    )

    logging.debug("Done loading!")

    INSTRUCTION = "List the MITRE techniques contained in the text."

    template = {"instruction": INSTRUCTION, "input": None, "output": None,"text":None}

    alpaca_text = "Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request. ### Instruction: {0} ### Input: {1} ### Response: {2}."
    samples = []

    logging.debug("Generating training set via sentence split")

    with tqdm(total=len(attck.enterprise.techniques)) as pbar:
        for technique in attck.enterprise.techniques:
            tactic = technique.external_references[0].external_id
            phases = technique.kill_chain_phases
            description  = technique.description
            # split into sentences
            sent_spans = list(nlp_web_en(description).sents)
            for sent in sent_spans:
                text_sent = sent.text.strip()
                template['input'] =  text_sent
                template['output'] = tactic
                template['text'] = alpaca_text.format(INSTRUCTION,text_sent,tactic)

                samples.append(template.copy())

            pbar.update(1)

    with open("./modal/enterprise_attack.jsonl","w") as file:
        for sample in samples:
            file.write(json.dumps(sample))

    #push to hugging face
    api = HfApi()
    api.upload_file(
        path_or_fileobj="./modal/enterprise_attack.jsonl",
        path_in_repo="enterprise_attack.jsonl",
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

    if args.test_spacy:
        test_sentence()

    if args.gen_training:
        gen_enterprise_attck_alpaca()


