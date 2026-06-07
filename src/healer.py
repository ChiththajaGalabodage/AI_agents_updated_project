from __future__ import annotations

import re
import time
from typing import Any

from src.output_format import parse_generation_bundle


def heal_test_bundle(
    current_test_code: str,
    test_output: str,
    analysis: dict[str, Any],
    ai_generator: Any | None = None,
) -> dict[str, Any]:
    """Try to heal generated test code after structural failures.

    Self-healing must not hide real product defects. The local fallback only
    fixes generated-test problems such as unresolved names or missing imports.
    Assertion failures and application exceptions are preserved so defect
    detection metrics remain valid for the research comparison.
    """
    if ai_generator is not None and getattr(ai_generator, "can_use_ai", False):
        prompt = (
            "The following pytest test file failed. Fix only generated-test defects and return ONLY a JSON object with exactly these keys:\n"
            "{\n"
            '  "test_code": ["import pytest", "...pytest code lines..."],\n'
            '  "explanation": ["concise bullet 1", "concise bullet 2"]\n'
            "}\n\n"
            "Rules:\n"
            "1. test_code must be a JSON array of strings containing executable pytest code.\n"
            "2. explanation must be a JSON array of short bullets describing the fix.\n"
            "3. Do not include markdown fences, prose, or extra keys.\n"
            "4. Preserve meaningful assertions that reveal product defects; do not replace them with non-null checks.\n\n"
            f"Failure output:\n{test_output}\n\n"
            f"Code analysis:\n{analysis}\n\n"
            f"Current tests:\n{current_test_code}"
        )
        max_retries = 3
        retry_delay_seconds = 5
        for attempt in range(1, max_retries + 1):
            try:
                response = ai_generator._client.models.generate_content(
                    model=ai_generator.model,
                    contents=prompt,
                )
                bundle = parse_generation_bundle(response.text or "")
                healed = bundle["test_code"].strip()
                if healed:
                    return bundle
                raise ValueError("Empty healing response from API")
            except Exception as error:
                print(f"Healer API Error (Attempt {attempt}/{max_retries}): {error}")
                if attempt < max_retries:
                    print(f"Retrying healer in {retry_delay_seconds} seconds...")
                    time.sleep(retry_delay_seconds)
                else:
                    print("Healer retries exhausted. Using local deterministic heal.")
                    break

    return _heal_structural_issues(current_test_code, test_output)


def heal_test_code(
    current_test_code: str,
    test_output: str,
    analysis: dict[str, Any],
    ai_generator: Any | None = None,
) -> str:
    return heal_test_bundle(
        current_test_code=current_test_code,
        test_output=test_output,
        analysis=analysis,
        ai_generator=ai_generator,
    )["test_code"]


def _heal_structural_issues(test_code: str, test_output: str) -> dict[str, Any]:
    unresolved_names = _extract_unresolved_names(test_output)
    if unresolved_names:
        healed = _remove_tests_referencing_names(test_code, unresolved_names)
        if healed != test_code:
            return {
                "test_code": _ensure_pytest_import(healed),
                "explanation": [
                    "Removed generated tests that referenced unavailable target-module symbols.",
                    "Preserved behavioral assertions so real defects remain visible in metrics.",
                ],
            }

    return {
        "test_code": _ensure_pytest_import(test_code),
        "explanation": [
            "No deterministic structural repair was safe to apply.",
            "Assertions were preserved to avoid masking application defects.",
        ],
    }


def _extract_unresolved_names(output: str) -> set[str]:
    names: set[str] = set()
    for match in re.finditer(r"NameError:\s+name ['\"]([^'\"]+)['\"] is not defined", output):
        names.add(match.group(1))
    for match in re.finditer(r"Unresolved test references:\s*([^\n]+)", output):
        for name in re.split(r"[,\s]+", match.group(1).strip()):
            if name:
                names.add(name.strip())
    return names


def _remove_tests_referencing_names(test_code: str, names: set[str]) -> str:
    lines = test_code.splitlines()
    result: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("def test_"):
            block = [line]
            index += 1
            while index < len(lines) and not lines[index].startswith("def test_"):
                block.append(lines[index])
                index += 1
            block_text = "\n".join(block)
            if any(re.search(rf"\b{re.escape(name)}\b", block_text) for name in names):
                continue
            result.extend(block)
            continue
        result.append(line)
        index += 1
    return "\n".join(result).rstrip() + "\n"


def _ensure_pytest_import(test_code: str) -> str:
    return test_code if "import pytest" in test_code else "import pytest\n" + test_code
