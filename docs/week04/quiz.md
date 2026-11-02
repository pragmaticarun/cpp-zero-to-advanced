# Week 4 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 4.1)* Why can't you call a non-const member function through a `const Volume&`?

??? question "Show answer"
    A const reference only allows operations that promise not to modify the object, i.e. `const` member functions.

**Q2.** *(from 4.1)* What's the type of `this` inside a `const` member function of `Volume`?

??? question "Show answer"
    `const Volume*`.

**Q3.** *(from 4.2)* How many elements does `std::vector<int> v{5};` have? And `std::vector<int> v(5);`?

??? question "Show answer"
    `{5}`: one element with value 5 (initializer_list). `(5)`: five zero-valued elements.

**Q4.** *(from 4.2)* A class declares `int a_; int b_;` and the constructor writes `: b_{1}, a_{b_}`. What's `a_`?

??? question "Show answer"
    Indeterminate (UB to read): `a_` is initialized first, from the not-yet-initialized `b_`. Initialization follows declaration order.

**Q5.** *(from 4.3)* Why does RAII make code exception-safe without try/catch at every call site?

??? question "Show answer"
    Destructors of local objects run during stack unwinding, so resources are released whatever path leaves the scope.

**Q6.** *(from 4.3)* What goes wrong if a `File` RAII class is copyable with the default copy constructor?

??? question "Show answer"
    Both copies hold the same `FILE*` and both destructors call `fclose` on it — a double close (UB).

**Q7.** *(from 4.4)* Why does `if (codec)` compile with an `explicit operator bool`, but `int n = codec;` doesn't?

??? question "Show answer"
    `if` performs a *contextual conversion* to bool, which is allowed to use explicit conversion operators. Copy-initialization of `int` would need an implicit conversion.

**Q8.** *(from 4.4)* Does a `static` member function have a `this` pointer?

??? question "Show answer"
    No; it isn't called on an object. It can access only static members (or objects passed to it).

**Q9.** *(from 4.5)* With only `bool operator==(const T&) const` defined, does `a != b` compile in C++20?

??? question "Show answer"
    Yes. C++20 rewrites `a != b` as `!(a == b)`.

**Q10.** *(from 4.5)* What comparison category does `double <=> double` return and why?

??? question "Show answer"
    `std::partial_ordering`, because NaN is unordered with respect to every value.

