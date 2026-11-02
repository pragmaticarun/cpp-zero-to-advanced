# Week 5 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 5.1)* What does the implicitly generated copy constructor do?

??? question "Show answer"
    Copy-constructs each base and member in declaration order (memberwise copy).

**Q2.** *(from 5.1)* Why is copy-and-swap safe for self-assignment?

??? question "Show answer"
    The parameter is a full copy made before anything in `*this` changes, so swapping with it is fine even if the source was `*this`.

**Q3.** *(from 5.2)* Classify: `v[0]` (vector<int> v), `v.size()`, `std::move(v)`, `"hello"`.

??? question "Show answer"
    `v[0]` lvalue (returns `int&`); `v.size()` prvalue; `std::move(v)` xvalue; a string literal is an lvalue (an array object with static storage).

**Q4.** *(from 5.2)* Inside `void f(Widget&& w)`, which overload does `g(w)` call: `g(const Widget&)` or `g(Widget&&)`?

??? question "Show answer"
    `g(const Widget&)`. `w` is a named variable, hence an lvalue. To call the `&&` overload write `g(std::move(w))`.

**Q5.** *(from 5.3)* What does `std::move` actually do?

??? question "Show answer"
    `static_cast<T&&>` — it converts its argument to an xvalue so move overloads can be selected. It performs no moving itself.

**Q6.** *(from 5.3)* Why might `std::vector<T>` copy elements during `push_back` even though `T` has a move constructor?

??? question "Show answer"
    If the move constructor isn't `noexcept` (and T is copyable), vector uses copies to keep the strong exception guarantee on reallocation (`std::move_if_noexcept`).

**Q7.** *(from 5.4)* Can a function return a non-copyable, non-movable type by value in C++17?

??? question "Show answer"
    Yes, if it returns a prvalue (`return T{...};`), thanks to guaranteed copy elision.

**Q8.** *(from 5.4)* Why can't the compiler apply NRVO in `if (b) return x; return y;`?

??? question "Show answer"
    There are two different named objects that might be returned, so neither can be constructed in the caller's storage in advance. The return falls back to an implicit move.

**Q9.** *(from 5.5)* Does `struct P { int x, y; }; P p{.y = 1, .x = 2};` compile in C++20?

??? question "Show answer"
    No — designators must appear in declaration order (`.x` before `.y`).

**Q10.** *(from 5.5)* In `for (auto& [k, v] : m)` over a `std::map`, can you modify `k`?

??? question "Show answer"
    No: map elements are `std::pair<const Key, T>`, so `k` refers to a const key. You can modify `v`.

