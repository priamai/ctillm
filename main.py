import json
import logging
logging.basicConfig(level=logging.DEBUG)
import spacy
from spacy.lang.en import English

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
def run_enterprise_attck():

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
    template = {"question": "Which is the MITRE technique?", "context": None, "answer": None}
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
                template['context'] =  text_sent
                template['answer'] = tactic
                samples.append(template.copy())

            pbar.update(1)

    with open("./modal-labs/enterprise_attack.jsonl","w") as file:
        for sample in samples:
            file.write(json.dumps(sample))
    logging.debug("Saved as JSONL")
import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-test_spacy", default=False,action="store_true")
    parser.add_argument("-gen_training", default=True, action="store_true")

    args = parser.parse_args()

    if args.test_spacy:
        test_sentence()
    if args.gen_training:
        run_enterprise_attck()
