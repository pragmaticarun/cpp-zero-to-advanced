#!/usr/bin/env python3
"""Compile (and run) every example listed in examples/manifest.json.

  --update   write .out files from the actual program output (used when authoring)
  default    compare program output with the committed .out files

Compiler: $CXX (default: g++ if available, else clang via `python3 -m ziglang c++`).
"""
import json, os, pathlib, shlex, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
update = "--update" in sys.argv
only = [a for a in sys.argv[1:] if not a.startswith("--")]
cxx = os.environ.get("CXX") or ("g++" if shutil.which("g++") else "python3 -m ziglang c++")
cxx = shlex.split(cxx)
man = json.loads((ROOT / "examples/manifest.json").read_text())
stats = dict(compiled=0, ran=0, output_ok=0, expected_fail_ok=0, unsupported=0, failed=0, san_skipped=0)
fails, unsup = [], []
tmp = pathlib.Path(tempfile.mkdtemp())
san_ok = {}


def san_supported(s):
    if s not in san_ok:
        t = tmp / "s.cpp"; t.write_text("int main(){}\n")
        r = subprocess.run(cxx + [f"-fsanitize={s}", str(t), "-o", str(tmp / "s")], capture_output=True)
        san_ok[s] = r.returncode == 0 and subprocess.run([str(tmp / "s")], capture_output=True).returncode == 0
    return san_ok[s]


for rel, m in sorted(man.items()):
    if only and not any(o in rel for o in only):
        continue
    src = ROOT / rel
    exe = tmp / (rel.replace("/", "_") + ".bin")
    base = cxx + [f"-std={m['std']}", "-Wall", "-Wextra", "-Wpedantic", "-pthread", *m["flags"]]
    sans = [s for s in m["san"] if san_supported(s)]
    if len(sans) < len(m["san"]):
        stats["san_skipped"] += 1
    flags = base + (["-g", "-fno-omit-frame-pointer", "-fsanitize=" + ",".join(sans)] if sans else ["-O1"])
    r = subprocess.run(flags + [str(src), "-o", str(exe)], capture_output=True, text=True)
    if m["expect"] == "fail":
        if r.returncode != 0:
            stats["expected_fail_ok"] += 1
        else:
            stats["failed"] += 1; fails.append((rel, "expected compile failure but it compiled"))
        continue
    if m["expect"] == "san-detect":
        if r.returncode != 0:
            stats["failed"] += 1; fails.append((rel, r.stderr[-1500:])); continue
        stats["compiled"] += 1
        if not sans:
            continue
        p = subprocess.run([str(exe)], capture_output=True, text=True, timeout=30)
        if p.returncode != 0 and any(k in p.stderr for k in ("Sanitizer", "runtime error", "panic:")):
            stats["sanitizer_detected_ok"] = stats.get("sanitizer_detected_ok", 0) + 1
        else:
            stats["failed"] += 1; fails.append((rel, "sanitizer did not detect the bug"))
        continue
    if r.returncode != 0:
        if m["maybe_unsupported"]:
            stats["unsupported"] += 1; unsup.append(rel); continue
        stats["failed"] += 1; fails.append((rel, r.stderr[-1500:])); continue
    stats["compiled"] += 1
    if r.stderr.strip() and "_starter" not in rel:
        fails.append((rel, "WARNINGS:\n" + r.stderr[-1500:])); stats["failed"] += 1; continue
    if not m["run"]:
        continue
    try:
        p = subprocess.run([str(exe)], capture_output=True, text=True, timeout=30, input="")
    except subprocess.TimeoutExpired:
        stats["failed"] += 1; fails.append((rel, "timeout")); continue
    if p.returncode != 0 or "runtime error" in p.stderr or "Sanitizer" in p.stderr:
        stats["failed"] += 1; fails.append((rel, f"exit {p.returncode}\n{p.stderr[-1500:]}")); continue
    stats["ran"] += 1
    out = ROOT / (rel[:-4] + ".out")
    if update or not out.exists():
        out.write_text(p.stdout); stats["output_ok"] += 1
    elif not m["compare"] or out.read_text() == p.stdout:
        stats["output_ok"] += 1
    else:
        stats["failed"] += 1; fails.append((rel, f"output differs:\n--- expected\n{out.read_text()}\n--- got\n{p.stdout}"))

for rel, msg in fails:
    print(f"FAIL {rel}\n{msg}\n")
for rel in unsup:
    print(f"NOT COMPILED HERE (compiler/library lacks feature): {rel}")
print("compiler:", " ".join(cxx), "| sanitizers available:", {k: v for k, v in san_ok.items()})
print("SUMMARY", json.dumps(stats))
sys.exit(1 if stats["failed"] else 0)
