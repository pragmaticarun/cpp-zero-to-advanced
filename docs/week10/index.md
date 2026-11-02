# Week 10: The standard library I: containers and iterators

Choosing the right container is one of the highest-leverage decisions in C++ — often worth more than any
micro-optimization. This week tours every standard container, explains its complexity and memory layout,
and gives you a decision procedure. The short version, which we'll justify with measurements:
**default to `std::vector`.**

| # | Lesson | Standard | Length |
|---|---|---|---|
| 10.1 | [std::vector in depth](lesson01.md) | C++20 | 12 min |
| 10.2 | [array, deque, list, and forward_list](lesson02.md) | C++20 | 10 min |
| 10.3 | [Associative and unordered containers](lesson03.md) | C++20 | 12 min |
| 10.4 | [Container adaptors, flat_map and flat_set](lesson04.md) | C++23 | 10 min |
| 10.5 | [Views over data: span, mdspan, string_view, and inplace_vector (preview)](lesson05.md) | C++23 | 11 min |
| 10.6 | [Iterators and iterator categories](lesson06.md) | C++20 | 11 min |

When you're done with the lessons, take the [week quiz](quiz.md) and the [programming assignment](assignment.md).
