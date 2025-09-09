from drug_resources import drugs, drug_concepts_with_short_name, dosage_forms
from uuid import uuid4

drug_concept_map = {}
dosage_form_map = {}

for drug_concept_uuid, drug_concept_name, short_name in drug_concepts_with_short_name:
    drug_concept_map[drug_concept_name.lower()] = drug_concept_uuid
    if short_name and short_name != "":
        drug_concept_map[short_name.lower()] = drug_concept_uuid

for dosage_form_uuid, dosage_form_name in dosage_forms:
    dosage_form_map[dosage_form_name] = dosage_form_uuid


def get_concept_uuid(drug_concept_name):
    drug_concept_name = drug_concept_name.lower()
    if "(" not in drug_concept_name or ")" not in drug_concept_name:
        return drug_concept_map.get(drug_concept_name)

    wo_paranthesis = " ".join(
        part.strip() for part in drug_concept_name.split("(")[0].split(")")
    ).strip()
    only_paranthesis = drug_concept_name.split("(")[1].split(")")[0].strip()
    return (
        drug_concept_map.get(drug_concept_name)
        or drug_concept_map.get(wo_paranthesis)
        or drug_concept_map.get(only_paranthesis)
    )


def get_dosage_form_uuid(drug_dosage_form):
    drug_dosage_form = drug_dosage_form.replace(
        r"\(.*?\)",
        "",
    ).strip()
    return dosage_form_map.get(drug_dosage_form)


print(
    '"uuid","name","drug_concept_name","drug_concept_uuid","drug_dosage_form","drug_dosage_form_uuid","strength"'
)


for drug_name, drug_concept_name, drug_dosage_form, strength in drugs:
    drug_concept_uuid = get_concept_uuid(drug_concept_name)
    drug_dosage_form_uuid = get_dosage_form_uuid(drug_dosage_form)
    print(
        f'"{uuid4()}","{drug_name}","{drug_concept_name}","{drug_concept_uuid if drug_concept_uuid else "DrugConcept not found"}","{drug_dosage_form}","{drug_dosage_form_uuid if drug_dosage_form_uuid else "Dosage form not found"}","{strength}"'
    )
