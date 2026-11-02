# How to take this course

Welcome! Here's how to get the most out of this course.

## Pace

There are 16 weeks. At roughly **5–7 hours per week** (lessons + labs + assignment) you'll finish in about
four months. If you already know some C++, you can move faster through Weeks 1–3 — but do take the quizzes.
If you get a quiz question wrong, that's the lesson to revisit.

## Type the code

Reading code feels like understanding. Typing it, changing it, and breaking it *is* understanding.
For each lesson, open the example in your editor (they're all in the repository under
`examples/weekNN/`), run it, then change one thing and predict what will happen before you run it again.

## What's optional

Not everything is equally important on a first pass. Lessons and sections marked **optional** or
**advanced** can be skipped and revisited later:

- Week 6.4 (multiple and virtual inheritance) — good to know, rarely needed.
- Week 7.5 (SFINAE) — mostly historical; concepts replaced it. Learn to *read* it.
- Week 14 (memory orderings, lock-free) — genuinely hard. Don't worry if it takes two passes. Most
  professionals use mutexes and stay happy.
- Week 16.5 (C++26 preview) — the future, not yet in your compiler.

## Be honest with yourself about difficulty

C++ is a large language. Some topics (value categories, the memory model, template error messages) are
confusing for *everyone* at first. If something doesn't click, that's normal. Move on, come back after a
week, and it'll usually make much more sense.

## How the code is verified

Every example is a real `.cpp` file in the repository, included verbatim into the pages. A script
(`scripts/check_examples.sh`) compiles each one with `-Wall -Wextra -Wpedantic` and the right `-std=`, runs
it, and compares the output with what's shown on the page. Examples meant to show a compile error are
checked to actually fail. Concurrency examples are also run under ThreadSanitizer and UB examples under
AddressSanitizer/UBSan in CI. Short snippets inside the prose (marked as fragments, like
`int x;  // WRONG`) are illustrations, not full programs.

## Get help

- [cppreference.com](https://en.cppreference.com) is the reference you'll use daily.
- [Compiler Explorer](https://godbolt.org) to experiment.
- See [Sources & further reading](sources.md) for books and talks.
