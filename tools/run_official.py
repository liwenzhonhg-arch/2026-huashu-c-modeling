import argparse
import hashlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="隔离执行 C 题正式程序，验证后原子完成运行目录")
    parser.add_argument("--case-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--code", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--max-runtime-seconds", type=float)
    args = parser.parse_args()

    case_root = Path(args.case_root).resolve()
    code = Path(args.code).resolve()
    final = Path(args.run_dir).resolve()
    run_id = final.name + "-" + uuid.uuid4().hex[:12]
    staging = final.with_name(final.name + f".staging-{run_id}")
    incomplete = final.with_name(final.name + ".incomplete")
    for path in (final, staging, incomplete):
        if path.exists():
            raise FileExistsError(f"RUNNER-001: target already exists: {path}")
    (staging / "output" / "code").mkdir(parents=True)
    (staging / "output" / "code" / "solution.py").write_bytes(code.read_bytes())

    env = os.environ.copy()
    env["MMW_OUTPUT_ROOT"] = str(staging / "output")
    env["MMW_DATA_DIR"] = str(case_root / "附件数据")
    env["MMW_RUN_ID"] = run_id
    if args.max_runtime_seconds is None:
        env.pop("MMW_MAX_RUNTIME_SECONDS", None)
    else:
        env["MMW_MAX_RUNTIME_SECONDS"] = str(args.max_runtime_seconds)
    command = [sys.executable, str(code)]
    started = __import__("time").time()
    completed = subprocess.run(command, cwd=case_root, env=env, text=True, encoding="utf-8", errors="replace", capture_output=True)
    (staging / "run_stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (staging / "run_stderr.txt").write_text(completed.stderr, encoding="utf-8")
    runner = {
        "run_id": run_id, "command": command, "exit_code": completed.returncode,
        "elapsed_seconds": __import__("time").time() - started,
        "code_sha256": sha256(code), "explicit_max_runtime_seconds": args.max_runtime_seconds,
    }
    (staging / "runner_status.json").write_text(json.dumps(runner, ensure_ascii=False, indent=2), encoding="utf-8")

    if completed.returncode == 0:
        validation = subprocess.run(
            [sys.executable, str(case_root / "validate_results.py"), str(staging), "--run-only"],
            cwd=case_root, text=True, encoding="utf-8", errors="replace", capture_output=True,
        )
        (staging / "validation_stdout.txt").write_text(validation.stdout, encoding="utf-8")
        (staging / "validation_stderr.txt").write_text(validation.stderr, encoding="utf-8")
        if validation.returncode != 0:
            runner["validation_exit_code"] = validation.returncode
            (staging / "runner_status.json").write_text(json.dumps(runner, ensure_ascii=False, indent=2), encoding="utf-8")
            os.replace(staging, incomplete)
            raise SystemExit(validation.returncode)
        runner["validation_exit_code"] = 0
        runner["status"] = "completed_and_validated"
        (staging / "runner_status.json").write_text(json.dumps(runner, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(staging, final)
        print(json.dumps({"status": "completed", "run_dir": str(final), **runner}, ensure_ascii=False, indent=2))
        return

    runner["status"] = "external_timeout" if completed.returncode == 124 else "failed"
    (staging / "runner_status.json").write_text(json.dumps(runner, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(staging, incomplete)
    print(json.dumps({"status": runner["status"], "run_dir": str(incomplete), **runner}, ensure_ascii=False, indent=2))
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
