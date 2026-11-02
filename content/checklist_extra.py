INTRO = """
This page lists the important C++ language features and standard library topics, each mapped to the lesson
that teaches it and tagged with the standard that introduced it (or made it usable in its modern form).
It is **generated from the lesson sources**, so if a row is here, the lesson really covers it.

Tags: **C++98/03** (classic), **C++11**, **C++14**, **C++17**, **C++20**, **C++23**, **C++26 (preview)**.
A "—" tag means a tool or practice rather than a language feature.

Use it as a checklist: tick off what you can explain to a colleague without notes.
"""
OUTRO = """
## C++26 preview items

C++26 was finalized in 2025–2026; compilers are still implementing it. These are covered in
[Lesson 16.5: C++26 preview](../week16/lesson05.md):

| Feature | Status |
|---|---|
| Static reflection (`^^T`, `std::meta`, splicers `[: :]`) | C++26 (P2996) — preview, experimental compilers only |
| Contracts (`pre`, `post`, `contract_assert`) | C++26 (P2900) — preview |
| `std::execution` (senders/receivers) | C++26 (P2300) — preview; usable today via NVIDIA stdexec |
| `std::inplace_vector` | C++26 (P0843) — preview |
| `#embed`, pack indexing, `= delete("reason")`, placeholder `_` variables | C++26 — preview |
| Hardened standard library, erroneous behaviour for uninitialized reads | C++26 — preview |
"""
NAV_HEAD = [{"Home": "index.md"}, {"How to take this course": "how-to-take.md"},
            {"Setup": "setup.md"}, {"Feature checklist": "curriculum/feature-checklist.md"}]
NAV_TAIL = [{"Capstones": [{"Capstone overview": "capstone/index.md"},
                           {"A: Concurrent task library + CLI": "capstone/threadpool.md"},
                           {"B: Embedded ring buffer": "capstone/ringbuffer.md"}]},
            {"Sources & further reading": "sources.md"}, {"License": "license.md"}]
