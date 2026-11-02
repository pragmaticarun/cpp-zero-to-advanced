# Week 9 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 9.1)* Why catch by `const&` rather than by value?

??? question "Show answer"
    Catching by value copies and slices derived exceptions to the caught type; a reference preserves the dynamic type and avoids the copy.

**Q2.** *(from 9.1)* What happens if an exception is never caught?

??? question "Show answer"
    `std::terminate` is called.

**Q3.** *(from 9.2)* What guarantee does `add_bad` provide?

??? question "Show answer"
    Not even the basic guarantee in a meaningful sense: the class invariant (count == size) is broken after the exception.

**Q4.** *(from 9.2)* Why does `std::vector` care whether your move constructor is `noexcept`?

??? question "Show answer"
    To keep push_back's strong guarantee during reallocation: if a move could throw midway, the old buffer would be partially moved-from, so it copies instead.

**Q5.** *(from 9.3)* What happens on `*opt` when `opt` is empty?

??? question "Show answer"
    Undefined behaviour. Use `value()` (throws) or check first.

**Q6.** *(from 9.3)* What's the difference between `and_then` and `transform` on optional?

??? question "Show answer"
    `transform` maps the value with a function returning a plain value; `and_then` takes a function that itself returns an optional, flattening the result.

**Q7.** *(from 9.4)* How do you return an error from a function returning `std::expected<int, std::string>`?

??? question "Show answer"
    `return std::unexpected{std::string{"message"}};` (or `std::unexpected("message")` where convertible).

**Q8.** *(from 9.4)* Why compare `ec == std::errc::no_such_file_or_directory` instead of `ec.value() == 2`?

??? question "Show answer"
    The comparison goes through error categories/conditions and is portable; raw values differ between platforms and categories.

**Q9.** *(from 9.5)* Why can `x + 1 < x` be optimized to `false`?

??? question "Show answer"
    Signed overflow is UB, so the compiler may assume it doesn't happen; then `x + 1` is always greater than `x`.

**Q10.** *(from 9.5)* Is the order of evaluation of function arguments undefined, unspecified or implementation-defined?

??? question "Show answer"
    Unspecified — the compiler can pick any order and need not document it; it's not UB by itself.

