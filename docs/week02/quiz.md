# Week 2 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 2.1)* What's wrong with `for (auto x : v) x = 0;`?

??? question "Show answer"
    `x` is a copy of each element, so the vector is unchanged. Use `auto& x`.

**Q2.** *(from 2.1)* Where is `it` visible in `if (auto it = m.find(k); it != m.end()) {...} else {...}`?

??? question "Show answer"
    In the condition, the `if` body *and* the `else` body, but not after the whole statement.

**Q3.** *(from 2.2)* Given `void f(int); void f(double);`, which is called by `f('a')`? By `f(1.0f)`?

??? question "Show answer"
    `f(int)` (char→int is an integral promotion) and `f(double)` (float→double is a floating-point promotion).

**Q4.** *(from 2.2)* Why might changing a default argument in a library header not affect an already-compiled app?

??? question "Show answer"
    Defaults are inserted at each call site at compile time, so the app keeps the old value until recompiled.

**Q5.** *(from 2.3)* Why can't `void f(std::string& s)` be called as `f(std::string{"x"})`?

??? question "Show answer"
    A non-const lvalue reference can't bind to a temporary (an rvalue). Use `const std::string&` (or `std::string&&` / by value if you want to consume it).

**Q6.** *(from 2.3)* Given `const std::vector<int>& r = v;`, what is the type of `auto x = r;`?

??? question "Show answer"
    `std::vector<int>` — a full copy, because `auto` drops the reference and top-level const.

**Q7.** *(from 2.4)* In what order are three local objects `a`, `b`, `c` destroyed?

??? question "Show answer"
    `c`, `b`, `a` — reverse order of construction.

**Q8.** *(from 2.4)* What is the static initialization order fiasco and one fix?

??? question "Show answer"
    Globals in different translation units are initialized in unspecified order, so one global's constructor may use another before it's initialized. Fix: replace the global with a function returning a reference to a function-local static (construct on first use), or use `constinit`/`constexpr` for constant initialization.

**Q9.** *(from 2.5)* Name two problems with unscoped enums that `enum class` fixes.

??? question "Show answer"
    Unscoped enumerators leak into the enclosing scope (name clashes), and they implicitly convert to `int` (allowing nonsense arithmetic/comparisons between unrelated enums).

**Q10.** *(from 2.5)* How do you get the integer value of an `enum class` in C++23?

??? question "Show answer"
    `std::to_underlying(e)` from `<utility>` (or `static_cast<std::underlying_type_t<E>>(e)` before C++23).

