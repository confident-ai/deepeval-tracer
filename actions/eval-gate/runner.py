import json
import os
import sys
import urllib.request
from enum import Enum
from typing import Dict, List

BASE = os.environ["CONFIDENT_BASE_URL"].rstrip("/")
API_KEY = os.environ.get("CONFIDENT_API_KEY", "")
ALIAS = os.environ["DATASET_ALIAS"]
VERSION = os.environ.get("DATASET_VERSION") or "latest"


class RefType(str, Enum):
    PULL_REQUEST = "PULL_REQUEST"
    BRANCH = "BRANCH"


def headers() -> Dict[str, str]:
    return {"Content-Type": "application/json", "confident-api-key": API_KEY}


def git_context() -> Dict[str, object]:
    repo = os.environ.get("REPO", "/")
    owner, _, name = repo.partition("/")
    pr = os.environ.get("PR_NUMBER") or ""
    return {
        "repoOwner": owner,
        "repoName": name,
        "repoId": int(os.environ.get("REPO_ID") or 0),
        "refType": (RefType.PULL_REQUEST if pr else RefType.BRANCH).value,
        "prNumber": int(pr) if pr else None,
        "headSha": os.environ.get("HEAD_SHA") or "",
        "baseBranch": os.environ.get("BASE_BRANCH") or "",
    }


def post(payload: Dict[str, object]) -> Dict[str, object]:
    req = urllib.request.Request(
        BASE + "/v1/eval-gate/runs",
        data=json.dumps(payload).encode(),
        headers=headers(),
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def pull_goldens() -> List[Dict[str, object]]:
    url = BASE + "/v1/datasets/" + ALIAS + "?version=" + VERSION
    req = urllib.request.Request(url, headers=headers(), method="GET")
    with urllib.request.urlopen(req, timeout=120) as r:
        body = json.loads(r.read().decode())
    body = body.get("data", body)
    return body.get("goldens", [])


def report_crash(error: str) -> None:
    print("eval-gate: app failure: " + str(error), file=sys.stderr)
    try:
        post({"git": git_context(), "execution": {"crashed": True, "error": str(error)}})
    except Exception as e:
        print("eval-gate: failed to report crash: " + str(e), file=sys.stderr)
    sys.exit(1)


def main() -> None:
    sys.path.insert(0, os.getcwd())
    try:
        from confident_eval import run
    except Exception as e:
        report_crash("could not import confident_eval.run: " + str(e))
        return

    try:
        goldens = pull_goldens()
    except Exception as e:
        report_crash("could not pull dataset: " + str(e))
        return

    test_cases = []
    try:
        for golden in goldens:
            inp = golden.get("input")
            output = run(inp)
            case = {"input": inp, "actualOutput": output}
            if golden.get("expectedOutput") is not None:
                case["expectedOutput"] = golden["expectedOutput"]
            if golden.get("retrievalContext") is not None:
                case["retrievalContext"] = golden["retrievalContext"]
            if golden.get("context") is not None:
                case["context"] = golden["context"]
            test_cases.append(case)
    except Exception as e:
        report_crash("app raised while producing outputs: " + str(e))
        return

    resp = post({"git": git_context(), "llmTestCases": test_cases})
    print(json.dumps(resp))


if __name__ == "__main__":
    main()
