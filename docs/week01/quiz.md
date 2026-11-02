# Week 1 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 1.1)* What does `return 0;` from `main` mean?

??? question "Show answer"
    It reports success to the operating system. Non-zero means failure. In `main` (and only `main`) you may omit it, and it behaves as `return 0;`.

**Q2.** *(from 1.1)* Does `-Wall` enable all warnings?

??? question "Show answer"
    No. Despite its name it enables a common set. `-Wextra` adds more, and there are still others (like `-Wconversion`) that you turn on separately.

**Q3.** *(from 1.2)* You get `undefined reference to 'foo()'`. Is this a compiler or linker error, and what are two likely causes?

??? question "Show answer"
    A linker error. Either the `.cpp` defining `foo` wasn't compiled/linked into the program, or the declaration and definition don't match (different parameter types, namespace, or `extern "C"` mismatch).

**Q4.** *(from 1.2)* Why does `int x = 5;` in a header cause trouble, but `inline int x = 5;` doesn't?

??? question "Show answer"
    Each TU that includes the header gets its own definition of `x`, violating the ODR (multiple definitions at link time). `inline` allows identical definitions in multiple TUs; the linker merges them.

**Q5.** *(from 1.3)* Is `sizeof(long)` always 8 on 64-bit systems?

??? question "Show answer"
    No. It's 8 on 64-bit Linux/macOS/Android (LP64) but 4 on 64-bit Windows (LLP64).

**Q6.** *(from 1.3)* Why does `std::cout << std::uint8_t{65}` print `A`?

??? question "Show answer"
    `std::uint8_t` is typically an alias for `unsigned char`, and the stream prints character types as characters. Cast to `int` first, or use `std::format`/`std::print` (Week 12), which format `unsigned char` as a number.

**Q7.** *(from 1.4)* Does `int n{3.5};` compile?

??? question "Show answer"
    No. List-initialization forbids narrowing from `double` to `int`. `int n = 3.5;` compiles (truncating to 3), typically with a warning under `-Wconversion`.

**Q8.** *(from 1.4)* What's the difference between `const int a = f();` and `constexpr int b = f();`?

??? question "Show answer"
    `a` can be initialized at run time; it just can't be modified afterwards. `b` requires `f()` to be evaluable at compile time (a `constexpr` function with constant arguments), otherwise it's a compile error.

**Q9.** *(from 1.5)* Why is `x + 1 < x` a bad overflow check for `int x`?

??? question "Show answer"
    Signed overflow is undefined behaviour, so the compiler may assume it never happens and simplify the expression to `false`. Check against `INT_MAX` before adding instead.

**Q10.** *(from 1.5)* What type and value does `std::uint8_t{250} + std::uint8_t{10}` have?

??? question "Show answer"
    `int` with value 260, because of integer promotion.

