# C++ from Zero to Advanced

A 16-week, intuition-first C++ course (C++20/23, with a C++26 preview), published at
**https://pragmaticarun.github.io/cpp-zero-to-advanced/**.

- `content/weekNN.py` — lesson sources (prose, quizzes, code)
- `scripts/gen.py` — generates `docs/` pages and `examples/` files
- `examples/` — every code example as a real file (+ `.out` expected output)
- `scripts/check_examples.sh` — compiles/runs all examples and checks output
- `docs/` — MkDocs Material site

```bash
pip install mkdocs-material
python3 scripts/gen.py
scripts/check_examples.sh          # or --update to refresh .out files
mkdocs serve
```

License: text CC BY 4.0, code MIT (see LICENSE).
