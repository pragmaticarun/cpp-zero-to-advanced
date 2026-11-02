# Week 4: Classes and RAII

This week we design our own types. A class bundles data with the operations that keep that data valid.
We'll see constructors and destructors, the (many!) ways C++ initializes objects, and then the single most
important idiom in the language: **RAII**, which ties resource cleanup to object lifetime.

If you only remember one thing from this course, make it RAII. It's why well-written C++ rarely leaks,
even without a garbage collector.

| # | Lesson | Standard | Length |
|---|---|---|---|
| 4.1 | [Classes, encapsulation, and const member functions](lesson01.md) | C++20 | 10 min |
| 4.2 | [Constructors, destructors, and every way to initialize](lesson02.md) | C++20 | 12 min |
| 4.3 | [RAII: tying resources to object lifetime](lesson03.md) | C++20 | 12 min |
| 4.4 | [explicit, conversions, static members, friends, nested classes](lesson04.md) | C++20 | 11 min |
| 4.5 | [Operator overloading and the spaceship operator <=>](lesson05.md) | C++23 | 12 min |

When you're done with the lessons, take the [week quiz](quiz.md) and the [programming assignment](assignment.md).
