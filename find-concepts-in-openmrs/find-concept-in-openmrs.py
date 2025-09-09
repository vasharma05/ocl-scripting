import requests
from typing import List, Dict, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from resources import (
    ConceptDefinition,
    CONCEPTS_TO_VALIDATE,
    CONCEPT_NAMES,
    validate_concept,
    default_concept_validator,
    OPENMRS_BASE_URL,
    OPENMRS_USERNAME,
    OPENMRS_PASSWORD,
    OPENMRS_COOKIES,
)


class OpenMRSConceptValidator:
    def __init__(self, base_url: str, cookies: dict, username: str, password: str):
        self.base_url = base_url
        self.auth = (username, password)
        self.cookies = cookies

    def validate_single_concept(
        self,
        concept: ConceptDefinition,
        custom_validator: Callable[[dict], bool] = None,
    ) -> Dict:
        """
        Validates a single concept against OpenMRS REST API
        Returns a dictionary with the validation result
        """
        # Search for concept by name
        response = requests.get(
            f"{self.base_url}/ws/rest/v1/concept",
            params={"q": concept.name},
            auth=self.auth,
            cookies=self.cookies,
        )

        if response.status_code != 200:
            return {"missing_concepts": [concept.name]}

        data = response.json()

        # Check if any results were found
        if not data.get("results"):
            return {"missing_concepts": [concept.name]}

        # Find exact name match
        found_concept = None
        for result in data["results"]:
            if any(
                name["display"].lower() == concept.name.lower()
                for name in result.get("names", [])
            ):
                found_concept = result
                break

        if not found_concept:
            return {"missing_concepts": [concept.name]}

        # Use custom validator if provided, otherwise use default validation
        validator = custom_validator if custom_validator else default_concept_validator

        if not validator(found_concept):
            return {"validation_failed": [concept.name]}

        return {
            "valid_concepts": [
                {
                    "name": concept.name,
                    "uuid": found_concept["uuid"],
                    "datatype": found_concept.get("datatype", {}).get("display"),
                }
            ]
        }

    def validate_single_concept_by_name(
        self, concept_name: str, custom_validator: Callable[[dict], bool] = None
    ) -> Dict:
        """
        Validates a single concept by name against OpenMRS REST API
        Returns a dictionary with the validation result
        """
        # Search for concept by name
        response = requests.get(
            f"{self.base_url}/openmrs/ws/rest/v1/concept",
            params={"q": concept_name},
            auth=self.auth,
            cookies=self.cookies,
        )

        if response.status_code != 200:
            return {"missing_concepts": [concept_name]}

        data = response.json()

        # Check if any results were found
        if not data.get("results"):
            return {"missing_concepts": [concept_name]}

        # Find exact name match
        found_concept = None
        for concept in data["results"]:
            if concept["display"].lower() == concept_name.lower():
                found_concept = concept
                break

        if not found_concept:
            return {"missing_concepts": [concept_name]}

        # Use custom validator if provided, otherwise use default validation
        validator = custom_validator if custom_validator else default_concept_validator

        if not validator(found_concept):
            return {"validation_failed": [concept_name]}

        return {
            "valid_concepts": [
                {
                    "name": concept_name,
                    "uuid": found_concept["uuid"],
                    "datatype": found_concept.get("datatype", {}).get("display"),
                }
            ]
        }

    def validate_concepts(
        self,
        concepts: List[ConceptDefinition],
        custom_validator: Callable[[dict], bool] = None,
    ) -> Dict:
        """
        Validates concepts against OpenMRS REST API using parallel threads
        Returns dictionary with validation results and missing concepts
        """
        validation_results = {
            "valid_concepts": [],
            "missing_concepts": [],
            "validation_failed": [],
        }

        with ThreadPoolExecutor(max_workers=min(10, len(concepts))) as executor:
            future_to_concept = {
                executor.submit(
                    self.validate_single_concept, concept, custom_validator
                ): concept
                for concept in concepts
            }

            for future in as_completed(future_to_concept):
                result = future.result()

                # Merge results into the main validation_results dictionary
                if "valid_concepts" in result:
                    validation_results["valid_concepts"].extend(
                        result["valid_concepts"]
                    )
                if "missing_concepts" in result:
                    validation_results["missing_concepts"].extend(
                        result["missing_concepts"]
                    )
                if "validation_failed" in result:
                    validation_results["validation_failed"].extend(
                        result["validation_failed"]
                    )

        return validation_results

    def validate_concept_names(
        self, concept_names: List[str], custom_validator: Callable[[dict], bool] = None
    ) -> Dict:
        """
        Validates an array of concept names against OpenMRS REST API using parallel threads
        Returns dictionary with validation results and missing concepts
        """
        validation_results = {
            "valid_concepts": [],
            "missing_concepts": [],
            "validation_failed": [],
        }

        with ThreadPoolExecutor(max_workers=min(10, len(concept_names))) as executor:
            future_to_name = {
                executor.submit(
                    self.validate_single_concept_by_name, name, custom_validator
                ): name
                for name in concept_names
            }

            for future in as_completed(future_to_name):
                result = future.result()

                # Merge results into the main validation_results dictionary
                if "valid_concepts" in result:
                    validation_results["valid_concepts"].extend(
                        result["valid_concepts"]
                    )
                if "missing_concepts" in result:
                    validation_results["missing_concepts"].extend(
                        result["missing_concepts"]
                    )
                if "validation_failed" in result:
                    validation_results["validation_failed"].extend(
                        result["validation_failed"]
                    )

        return validation_results


if __name__ == "__main__":
    validator = OpenMRSConceptValidator(
        base_url=OPENMRS_BASE_URL,
        cookies=OPENMRS_COOKIES,
        username=OPENMRS_USERNAME,
        password=OPENMRS_PASSWORD,
    )

    # Validate concept names using the validate_concept function from resources.py
    print("=== Validating Concept Names ===")
    print(f"Validating {len(CONCEPT_NAMES)} concepts: {', '.join(CONCEPT_NAMES)}")

    results = validator.validate_concept_names(CONCEPT_NAMES, validate_concept)

    print(f"\n✅ Valid Concepts ({len(results['valid_concepts'])}):")
    for concept in results["valid_concepts"]:
        print(
            f"  - {concept['name']} (UUID: {concept['uuid']}, Type: {concept['datatype']})"
        )

    print(f"\n❌ Missing Concepts ({len(results['missing_concepts'])}):")
    for concept in results["missing_concepts"]:
        print(f"  - {concept}")

    print(f"\n⚠️  Validation Failed ({len(results['validation_failed'])}):")
    for concept in results["validation_failed"]:
        print(f"  - {concept}")

    # Summary
    total_concepts = len(CONCEPT_NAMES)
    valid_count = len(results["valid_concepts"])
    missing_count = len(results["missing_concepts"])
    failed_count = len(results["validation_failed"])

    print(f"\n📊 Summary:")
    print(f"  Total concepts: {total_concepts}")
    print(f"  Valid: {valid_count} ({valid_count/total_concepts*100:.1f}%)")
    print(f"  Missing: {missing_count} ({missing_count/total_concepts*100:.1f}%)")
    print(
        f"  Failed validation: {failed_count} ({failed_count/total_concepts*100:.1f}%)"
    )
