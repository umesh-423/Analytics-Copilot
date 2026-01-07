import json
from rag.answer_pipeline import answer

def load_tests(path: str = "eval/questions.jsonl"):
    tests = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tests.append(json.loads(line))
    return tests

def main():
    tests = load_tests()
    results = []

    for t in tests:
        q = t.get("question")
        expected_kpi = t.get("expected_kpi")
        should_refuse = bool(t.get("should_refuse"))

        out = None
        status = "unknown"
        predicted_kpi = None
        err = None
        passed = False

        try:
            out = answer(q)
            status = out.get("status", "unknown")
            predicted_kpi = out.get("kpi")
            err = out.get("error")

            if should_refuse:
                passed = (status == "refused")
            else:
                passed = (predicted_kpi == expected_kpi) and (status != "error")

        except Exception as e:
            status = "error"
            predicted_kpi = None
            err = str(e)
            passed = should_refuse  # If we expected refusal, exception counts as pass

        results.append({
            "question": q,
            "expected_kpi": expected_kpi,
            "predicted_kpi": predicted_kpi,
            "status": status,
            "error": err,
            "passed": passed,
        })

    print("\nEvaluation Results\n" + "-" * 22)
    passed_cnt = 0

    for r in results:
        mark = "PASS" if r["passed"] else "FAIL"
        suffix = f" | err={r['error']}" if r.get("error") else ""
        print(f"[{mark}] {r['question']} → {r['status']}{suffix}")
        if r["passed"]:
            passed_cnt += 1

    total = len(results)
    print(f"\nScore: {passed_cnt}/{total} passed")

if __name__ == "__main__":
    main()
