# Lesson 9.5: Assertions, contracts preview, and the undefined behaviour catalogue

<span class="stdtag">C++23</span> · about 14 minutes

## Why this matters

Undefined behaviour (UB) is the scariest phrase in C++. It doesn't mean "crashes"; it means *the standard
places no requirements* — the optimizer may assume it never happens, and your program can do anything,
including appear to work until the day it doesn't. This lesson is your field guide: what UB looks like,
how to catch it, and how assertions (and soon contracts) help you state your assumptions.

## Three kinds of "it depends"

| Term | Meaning | Example |
|---|---|---|
| Implementation-defined | each implementation picks and documents | `sizeof(long)`, right shift of negative ints (pre-C++20) |
| Unspecified | one of several valid outcomes, not documented | order of evaluation of function arguments |
| **Undefined** | no requirements at all | signed overflow, out-of-bounds access |

## The UB catalogue

| UB | Example | Catch it with |
|---|---|---|
| Out-of-bounds access | `v[v.size()]` | ASan, `-D_GLIBCXX_ASSERTIONS`, `.at()` |
| Use after free / dangling | reference to a destroyed local, iterator after `push_back` | ASan |
| Double free / mismatched `new[]`/`delete` | | ASan |
| Signed integer overflow | `INT_MAX + 1` | UBSan, constexpr tests |
| Shift too far / negative shift | `1 << 32` | UBSan |
| Reading uninitialized variables | `int x; use(x);` | MSan, `-Wuninitialized`, C++26 makes it "erroneous" |
| Null pointer dereference | | UBSan, ASan |
| Strict aliasing violation | `*(float*)&some_int` | `-fstrict-aliasing` warnings; use `std::bit_cast` |
| Data race | two threads, one writes, no sync | TSan |
| Misaligned access | casting a `char*` buffer to `int*` | UBSan |
| Modifying a `const` object | `const_cast` then write | — |
| Infinite loop without side effects | `while(true){}` with no I/O/atomics | — |
| Returning without a value from non-void | | `-Wreturn-type` |
| Violating `std::unreachable()` | | debug builds |

## Why the optimizer makes it worse

```cpp title="examples/week09/lesson05.cpp"
--8<-- "examples/week09/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week09/lesson05.out"
```

Because signed overflow is UB, the compiler may assume `x + 1 > x` is *always* true and delete your
overflow check. That's not a compiler bug; it's the contract you signed.

## Assertions

`assert(cond)` checks a condition in debug builds and is removed when `NDEBUG` is defined. Use it for
*internal invariants* — things that are true unless there's a bug. `static_assert` does the same at compile
time.

## Contracts (C++26 preview)

C++26 adds contract assertions as language syntax:

```cpp
int isqrt(int x)
    pre(x >= 0)
    post(r: r * r <= x);
// inside a body: contract_assert(cond);
```

The build chooses an *evaluation semantic* (ignore, observe, enforce, quick-enforce) and you can install a
violation handler. Compiler support is arriving in 2025–2026 (GCC trunk has an implementation); treat this
as a preview and keep using `assert` today.

!!! tip "Pro tip: the debug-build safety net"
    Add `-fsanitize=address,undefined -D_GLIBCXX_ASSERTIONS` (libstdc++) or `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_DEBUG`
    (libc++) to your test builds. Week 15 makes this a habit.

## Key takeaways

!!! success "Key takeaways"
    - UB means no requirements; optimizers assume it never happens and may delete your checks.
    - Check *before* an operation that could overflow; use `std::bit_cast` instead of type punning.
    - Use `assert` for internal invariants, `static_assert` for compile-time ones; contracts (C++26) are coming.
    - Run tests under ASan/UBSan/TSan and library hardening modes to catch UB early.

## Quiz

**Q1.** Why can `x + 1 < x` be optimized to `false`?

??? question "Show answer"
    Signed overflow is UB, so the compiler may assume it doesn't happen; then `x + 1` is always greater than `x`.

**Q2.** Is the order of evaluation of function arguments undefined, unspecified or implementation-defined?

??? question "Show answer"
    Unspecified — the compiler can pick any order and need not document it; it's not UB by itself.

**Q3.** What happens to `assert` in a release build with `-DNDEBUG`?

??? question "Show answer"
    It expands to nothing; the condition isn't evaluated (so never put side effects in an assert).

