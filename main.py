import json

from pyattck import Attck

from pyattck import Attck

# everything is the latest version
attck = Attck(
    nested_techniques=False,
    use_config=True,
    save_config=True,
    config_file_path='./pyattck/config.yml',
    data_path='./pyattck/data',
    enterprise_attck_json="https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json",
    pre_attck_json="https://raw.githubusercontent.com/mitre/cti/master/pre-attack/pre-attack.json",
    mobile_attck_json="https://raw.githubusercontent.com/mitre/cti/master/mobile-attack/mobile-attack.json",
    ics_attck_json="https://raw.githubusercontent.com/mitre/cti/master/ics-attack/ics-attack.json",
)

name_tactic = {}
for technique in attck.enterprise.techniques:
    print(technique.id)
    print(technique.name)

    tactic = technique.external_references[0].external_id

    phases = technique.kill_chain_phases

    name_tactic[tactic]=(technique.name,technique.description)

with open("enterprise_attack.json","w") as file:
    json.dump(name_tactic,file)


