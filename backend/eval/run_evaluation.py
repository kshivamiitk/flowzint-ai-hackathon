"""Run a small deterministic classifier benchmark.

Usage:
    cd backend
    python -m eval.run_evaluation
"""

import asyncio
import json
from pathlib import Path

from app.infrastructure.ai.local import LocalComplaintAnalyzer

DATASET = Path(__file__).with_name("scenarios.json")


async def main() -> None:
    analyzer = LocalComplaintAnalyzer()
    scenarios = json.loads(DATASET.read_text(encoding="utf-8"))

    intent_correct = 0
    severity_correct = 0
    rows: list[dict[str, str | bool]] = []

    for scenario in scenarios:
        result = await analyzer.analyze(scenario["message"])
        intent_match = result.intent.value == scenario["expected_intent"]
        severity_match = result.severity.value == scenario["expected_severity"]
        intent_correct += int(intent_match)
        severity_correct += int(severity_match)
        rows.append(
            {
                "message": scenario["message"],
                "intent": result.intent.value,
                "intent_ok": intent_match,
                "severity": result.severity.value,
                "severity_ok": severity_match,
            }
        )

    total = len(scenarios)
    print(
        json.dumps(
            {
                "cases": total,
                "intent_accuracy": round(intent_correct / total, 3),
                "severity_accuracy": round(severity_correct / total, 3),
                "results": rows,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
