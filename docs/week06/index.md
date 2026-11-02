# Week 6: Inheritance and runtime polymorphism

This week covers classic object-oriented C++: base and derived classes, virtual functions, and how the
compiler implements them with vtables. We'll also look at the traps — slicing, missing virtual
destructors — and at multiple inheritance and RTTI.

A modern perspective runs through the week: inheritance is a tool for *runtime polymorphism*, not for code
reuse. In Weeks 7–8 and 16 you'll see alternatives (templates, `std::variant`, type erasure) and learn when
each fits.

| # | Lesson | Standard | Length |
|---|---|---|---|
| 6.1 | [Inheritance basics: base classes, access, construction order](lesson01.md) | C++20 | 10 min |
| 6.2 | [Virtual functions, override, final, and how vtables work](lesson02.md) | C++20 | 12 min |
| 6.3 | [Abstract classes, interfaces, virtual destructors, and slicing](lesson03.md) | C++20 | 11 min |
| 6.4 | [Multiple and virtual inheritance (optional)](lesson04.md) | C++20 | 9 min |
| 6.5 | [RTTI: typeid, dynamic_cast, and std::any](lesson05.md) | C++20 | 9 min |

When you're done with the lessons, take the [week quiz](quiz.md) and the [programming assignment](assignment.md).
