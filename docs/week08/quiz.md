# Week 8 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 8.1)* What does `{ a + b } -> std::convertible_to<T>;` require?

??? question "Show answer"
    That `a + b` is a valid expression and its result type is convertible to `T`.

**Q2.** *(from 8.1)* Why did `advance_by` on a `std::vector` iterator choose the "jump" version?

??? question "Show answer"
    Both overloads match, but `std::random_access_iterator` subsumes `std::input_iterator`, so the more constrained overload wins.

**Q3.** *(from 8.2)* What's the difference between `constexpr` and `consteval` functions?

??? question "Show answer"
    `constexpr` functions *can* be evaluated at compile time; `consteval` functions *must* be (every call is a constant expression).

**Q4.** *(from 8.2)* Does `constinit` make a variable const?

??? question "Show answer"
    No — it only guarantees compile-time (static) initialization; the variable remains mutable.

**Q5.** *(from 8.3)* Why is `[&count]` dangerous in a returned lambda?

??? question "Show answer"
    The lambda outlives `count`, a local variable; calling it later reads a dangling reference (UB).

**Q6.** *(from 8.3)* Why did `copy()` print 1 while `counter` printed 1 then 2?

??? question "Show answer"
    `copy` was copied from `counter` before it was called, so it has its own independent `n`.

**Q7.** *(from 8.4)* Why can't `std::function` hold a lambda that captures a `std::unique_ptr`?

??? question "Show answer"
    `std::function` requires the callable to be copyable; such a lambda is move-only. Use `std::move_only_function`.

**Q8.** *(from 8.4)* When should a function take a template `F&&` instead of `std::function`?

??? question "Show answer"
    When it calls the callable immediately and doesn't store it — the template has no type-erasure overhead and inlines.

**Q9.** *(from 8.5)* What's the main limitation of CRTP vs virtual functions?

??? question "Show answer"
    No common base type: `Shape<Square>` and `Shape<Circle>` are unrelated, so you can't store them in one container and choose at run time.

**Q10.** *(from 8.5)* What does `template <typename Self> auto& get(this Self& self)` replace?

??? question "Show answer"
    A pair of overloads `T& get()` and `const T& get() const` (and possibly && versions).

