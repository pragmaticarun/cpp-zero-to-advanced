# Week 5: Value semantics: copy, move, and value categories

This is the week many people describe as "the moment C++ finally made sense". We'll look at what it
means to *copy* an object, then at **move semantics** — the C++11 feature that lets you transfer resources
instead of duplicating them — and the idea underneath it: *value categories*.

Honest warning: value categories are one of the most confusing topics in C++. We'll go slowly, with lots of
printed output so you can *see* which constructor runs. If it doesn't fully click this week, that's
completely normal; it'll click after you use it.

| # | Lesson | Standard | Length |
|---|---|---|---|
| 5.1 | [Copy semantics and the Rule of Three](lesson01.md) | C++20 | 11 min |
| 5.2 | [Value categories: lvalues, prvalues, xvalues](lesson02.md) | C++20 | 12 min |
| 5.3 | [Move semantics, std::move, and the Rules of Five and Zero](lesson03.md) | C++20 | 12 min |
| 5.4 | [Copy elision, RVO, and returning by value](lesson04.md) | C++20 | 9 min |
| 5.5 | [Aggregates, designated initializers, structured bindings, user-defined literals](lesson05.md) | C++20 | 11 min |

When you're done with the lessons, take the [week quiz](quiz.md) and the [programming assignment](assignment.md).
