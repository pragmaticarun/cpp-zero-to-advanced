# Week 7 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 7.1)* Why does `clamp_to(0.7, 0, 1)` fail?

??? question "Show answer"
    `T` is deduced as `double` from the first argument and `int` from the others; deduction fails because they conflict.

**Q2.** *(from 7.1)* Do templates have a runtime cost compared to hand-written overloads?

??? question "Show answer"
    No — instantiations are ordinary functions. The costs are compile time and code size.

**Q3.** *(from 7.2)* Why does `Window<std::string, 2>` compile even though `mean()` divides by `static_cast<std::string>(size())`?

??? question "Show answer"
    Member functions of class templates are only instantiated when used; `mean()` is never called.

**Q4.** *(from 7.2)* Can you partially specialize a function template?

??? question "Show answer"
    No. Only class (and variable) templates can be partially specialized; for functions use overloading or `if constexpr`.

**Q5.** *(from 7.3)* What does `(0 + ... + args)` evaluate to with no arguments?

??? question "Show answer"
    `0` — the initial value; without it, an empty `+` fold is ill-formed.

**Q6.** *(from 7.3)* How do you count the elements of a parameter pack?

??? question "Show answer"
    `sizeof...(Args)` (or `sizeof...(args)`).

**Q7.** *(from 7.4)* Is `void f(std::vector<T>&& v)` a forwarding reference?

??? question "Show answer"
    No — only plain `T&&` with `T` deduced is a forwarding reference; `std::vector<T>&&` is an rvalue reference.

**Q8.** *(from 7.4)* What is `T` when you call `template<class T> void f(T&&)` with an lvalue `int x`?

??? question "Show answer"
    `T = int&`, so the parameter type collapses to `int&`.

**Q9.** *(from 7.5)* Why can't a plain `if` replace `if constexpr` in `encode`?

??? question "Show answer"
    Both branches of a plain `if` must compile for every `T`; e.g. `value >> 8` doesn't compile for `std::string`.

**Q10.** *(from 7.5)* Why does `static_assert(sizeof(U) == 0, ...)` not fire for supported types?

??? question "Show answer"
    It's in a discarded `if constexpr` branch of a template and depends on `U`, so it's only evaluated when that branch is instantiated.

