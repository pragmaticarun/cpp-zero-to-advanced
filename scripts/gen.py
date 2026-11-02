#!/usr/bin/env python3
"""Generate docs/ pages and examples/ files from content/weekNN.py lesson specs.

Each content module defines WEEK = {num, title, intro, lessons:[...], assignment:{...}}.
Code lives in the spec, is written to examples/weekNN/*.cpp, and the docs pull it in
with pymdownx.snippets, so the page always shows exactly the file the checker compiled.
"""
import json, pathlib, runpy, re, textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS, EX, CONTENT = ROOT / "docs", ROOT / "examples", ROOT / "content"


def ded(s):
    return textwrap.dedent(s).strip("\n")


def code_block(path, lang="cpp", title=True):
    t = f' title="{path}"' if title else ""
    return f'```{lang}{t}\n--8<-- "{path}"\n```'


def main():
    manifest, nav_weeks, features = {}, [], []
    weeks = sorted(CONTENT.glob("week*.py"))
    for wf in weeks:
        W = runpy.run_path(str(wf))["WEEK"]
        n = W["num"]
        wdir = f"week{n:02d}"
        (DOCS / wdir).mkdir(parents=True, exist_ok=True)
        (EX / wdir).mkdir(parents=True, exist_ok=True)
        wnav = [{"Overview": f"{wdir}/index.md"}]
        lesson_rows = []
        for i, L in enumerate(W["lessons"], 1):
            slug = f"lesson{i:02d}"
            std = L.get("std", "C++20")
            # write example files
            files = dict(L.get("files", {}))
            fdefaults = {k: files.pop(k) for k in list(files) if k in ("std", "maybe_unsupported", "run", "compare", "san", "flags")}
            for name, spec in files.items():
                if isinstance(spec, str):
                    spec = {"code": spec}
                spec = {**fdefaults, **spec}
                fname = f"{slug}{name}.cpp" if not name.endswith(".cpp") else name
                rel = f"examples/{wdir}/{fname}"
                (ROOT / rel).write_text(ded(spec["code"]) + "\n")
                manifest[rel] = {
                    "std": spec.get("std", std).lower().replace("c++26", "c++2c"),
                    "run": spec.get("run", True),
                    "compare": spec.get("compare", True),
                    "san": spec.get("san", []),
                    "expect": spec.get("expect", "ok"),
                    "maybe_unsupported": spec.get("maybe_unsupported", False),
                    "flags": spec.get("flags", []),
                    "lesson": f"{wdir}/{slug}",
                }

            def expand(md):
                def rep(m):
                    name = m.group(1)
                    fname = f"{slug}{name}.cpp" if name != "" else f"{slug}.cpp"
                    rel = f"examples/{wdir}/{fname}"
                    meta = manifest[rel]
                    out = code_block(rel)
                    if meta["expect"] == "fail":
                        out = ('!!! failure "This one is supposed to fail to compile"\n'
                               "    The checker verifies the compiler rejects it.\n\n" + out)
                    elif meta["expect"] == "san-detect":
                        out = ('!!! bug "Deliberately buggy"\n'
                               f"    CI runs this under `-fsanitize={','.join(meta['san'])}` and checks the sanitizer reports the bug.\n\n" + out)
                    elif meta["run"]:
                        o = rel[:-4] + ".out"
                        note = "" if meta["compare"] else " (yours may differ: timing/threads)"
                        out += f'\n\n**Output**{note}:\n\n```text\n--8<-- "{o}"\n```'
                    return out
                return re.sub(r"\{\{ex:?([A-Za-z0-9_]*)\}\}", rep, ded(md))

            p = [f"# Lesson {n}.{i}: {L['title']}\n",
                 f'<span class="stdtag">{std}</span> · about {L.get("minutes", 10)} minutes\n',
                 "## Why this matters\n", ded(L["why"]), "", expand(L["body"]), ""]
            p += ["## Key takeaways\n", '!!! success "Key takeaways"']
            p += [f"    - {t}" for t in L["takeaways"]]
            p.append("")
            if L.get("quiz"):
                p.append("## Quiz\n")
                for qi, (q, a) in enumerate(L["quiz"], 1):
                    p.append(f"**Q{qi}.** {ded(q)}\n")
                    p.append('??? question "Show answer"')
                    p.append(textwrap.indent(ded(a), "    "))
                    p.append("")
            if L.get("lab"):
                lab = L["lab"]
                p += ["## Practice lab (optional)\n", ded(lab["task"]), ""]
                if "{{ex:" in lab.get("extra", ""):
                    pass
                for key, label in (("starter", "Starter code"), ("solution", "Full solution")):
                    if key in lab:
                        fname = f"{slug}_lab_{key}.cpp"
                        rel = f"examples/{wdir}/{fname}"
                        spec = lab[key] if isinstance(lab[key], dict) else {"code": lab[key]}
                        (ROOT / rel).write_text(ded(spec["code"]) + "\n")
                        manifest[rel] = {"std": spec.get("std", std).lower(), "run": spec.get("run", key == "solution"),
                                         "compare": spec.get("compare", True), "san": spec.get("san", []),
                                         "expect": "ok", "maybe_unsupported": spec.get("maybe_unsupported", False),
                                         "flags": spec.get("flags", []), "lesson": f"{wdir}/{slug}"}
                        blk = code_block(rel)
                        if key == "solution" and spec.get("run", True):
                            blk += f'\n\n**Output:**\n\n```text\n--8<-- "{rel[:-4]}.out"\n```'
                        tag = '???+ example' if key == "starter" else '??? tip'
                        p.append(f'{tag} "{label}"')
                        p.append(textwrap.indent(blk, "    "))
                        p.append("")
            (DOCS / wdir / f"{slug}.md").write_text("\n".join(p) + "\n")
            wnav.append({f"{n}.{i} {L['title']}": f"{wdir}/{slug}.md"})
            lesson_rows.append(f"| {n}.{i} | [{L['title']}]({slug}.md) | {std} | {L.get('minutes',10)} min |")
            for feat, fstd in L.get("features", []):
                features.append((L.get("area", W["title"]), feat, fstd, f"../{wdir}/{slug}.md", f"{n}.{i}"))
        # week overview + assignment
        A = W.get("assignment")
        ov = [f"# Week {n}: {W['title']}\n", ded(W["intro"]), "",
              "| # | Lesson | Standard | Length |", "|---|---|---|---|", *lesson_rows, ""]
        ov.append("When you're done with the lessons, take the [week quiz](quiz.md)"
                  + (" and the [programming assignment](assignment.md)." if A else "."))
        (DOCS / wdir / "index.md").write_text("\n".join(ov) + "\n")
        # week quiz: last quiz question of each lesson recombined + extra
        wq = [f"# Week {n} quiz\n", "Mixed review of the whole week. Try answering before you peek.\n"]
        k = 0
        for i, L in enumerate(W["lessons"], 1):
            for q, a in L.get("quiz", [])[:2]:
                k += 1
                wq += [f"**Q{k}.** *(from {n}.{i})* {ded(q)}\n", '??? question "Show answer"',
                       textwrap.indent(ded(a), "    "), ""]
        (DOCS / wdir / "quiz.md").write_text("\n".join(wq) + "\n")
        wnav.append({"Week quiz": f"{wdir}/quiz.md"})
        if A:
            ap = [f"# Week {n} programming assignment: {A['title']}\n", ded(A["task"]), ""]
            for key, label in (("starter", "Starter code"), ("solution", "Reference solution")):
                if key in A:
                    rel = f"examples/{wdir}/assignment_{key}.cpp"
                    spec = A[key] if isinstance(A[key], dict) else {"code": A[key]}
                    (ROOT / rel).write_text(ded(spec["code"]) + "\n")
                    manifest[rel] = {"std": spec.get("std", A.get("std", "c++20")).lower(), "run": key == "solution",
                                     "compare": spec.get("compare", True), "san": spec.get("san", []),
                                     "expect": "ok", "maybe_unsupported": spec.get("maybe_unsupported", False),
                                     "flags": spec.get("flags", []), "lesson": f"{wdir}/assignment"}
                    blk = code_block(rel)
                    if key == "solution":
                        blk += f'\n\n**Output:**\n\n```text\n--8<-- "{rel[:-4]}.out"\n```'
                    p2 = '???+ example' if key == "starter" else '??? tip'
                    ap += [f'{p2} "{label}"', textwrap.indent(blk, "    "), ""]
            (DOCS / wdir / "assignment.md").write_text("\n".join(ap) + "\n")
            wnav.append({"Programming assignment": f"{wdir}/assignment.md"})
        nav_weeks.append({f"Week {n}: {W['title']}": wnav})

    (EX / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True))
    # feature checklist
    extra = runpy.run_path(str(CONTENT / "checklist_extra.py"))
    rows = ["# Feature checklist\n", ded(extra["INTRO"]), ""]
    areas = {}
    for area, feat, fstd, link, num in features:
        areas.setdefault(area, []).append((feat, fstd, link, num))
    for area, items in areas.items():
        rows += [f"## {area}\n", "| Feature | Standard | Taught in |", "|---|---|---|"]
        for feat, fstd, link, num in items:
            rows.append(f"| {feat} | {fstd} | [Lesson {num}]({link}) |")
        rows.append("")
    rows.append(ded(extra["OUTRO"]))
    (DOCS / "curriculum").mkdir(exist_ok=True)
    (DOCS / "curriculum" / "feature-checklist.md").write_text("\n".join(rows) + "\n")
    # mkdocs.yml
    tmpl = (ROOT / "scripts" / "mkdocs.tmpl.yml").read_text()
    import yaml  # provided by mkdocs
    nav = yaml.safe_load(tmpl.split("#NAV")[1]) if False else None
    navy = yaml.safe_dump({"nav": [*extra["NAV_HEAD"], *nav_weeks, *extra["NAV_TAIL"]]},
                          sort_keys=False, allow_unicode=True)
    (ROOT / "mkdocs.yml").write_text(tmpl + "\n" + navy)
    print(f"weeks={len(weeks)} lessons={sum(len(list((DOCS/w).glob('lesson*.md'))) for w in [p.stem for p in weeks])} examples={len(manifest)} features={len(features)}")


if __name__ == "__main__":
    main()
