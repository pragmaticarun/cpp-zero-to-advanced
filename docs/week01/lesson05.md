# Lesson 1.5: Operators, integer promotion and narrowing

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

Quick puzzle: what does this print?

```cpp
std::vector<int> v;   // empty
if (-1 < v.size()) std::cout << "less"; else std::cout << "not less";
```

It prints **not less**. `-1` gets converted to an unsigned 64-bit number (a huge value) before the comparison.
This lesson explains the conversion rules that cause surprises like this, and the modern tools to avoid them.

## The everyday operators

You know most of these from other languages: `+ - * / %`, comparisons `== != < <= > >=`, logical
`&& || !`, assignment `= += -=` and friends, increment `++`/`--`. Two C++-specific notes:

- Integer division truncates toward zero: `-7 / 2 == -3`, and `-7 % 2 == -1`.
- `&&` and `||` short-circuit: in `p && p->ok()`, the right side isn't evaluated if `p` is null.

When precedence isn't obvious, add parentheses. Nobody remembers that `&` binds weaker than `==`.

## Integer promotion: small types become `int`

Before arithmetic, types smaller than `int` (`char`, `short`, `uint8_t`, `bool`) are *promoted* to `int`.
So `uint8_t a = 200, b = 100; auto c = a + b;` gives `c == 300` with type `int` — no overflow.

## Usual arithmetic conversions: the signed/unsigned trap

When you mix two different types, they're converted to a common type. The surprising rule: if one operand
is unsigned and at least as wide as the other, the **signed one is converted to unsigned**. That's the
`-1 < v.size()` puzzle: `-1` becomes `18446744073709551615`.

The fix, in C++20: `std::cmp_less`, `std::cmp_greater` etc. from `<utility>` compare integers *by value*,
regardless of signedness. Or just keep your types consistent (use `std::ssize(v)` for a signed size).

```cpp title="examples/week01/lesson05.cpp"
--8<-- "examples/week01/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week01/lesson05.out"
```

## Overflow: signed is UB, unsigned wraps

Unsigned arithmetic wraps around modulo 2ⁿ — that's well-defined. **Signed overflow is undefined
behaviour.** The optimizer is allowed to assume it never happens, which can delete your "overflow checks":

```cpp
bool will_overflow(int x) { return x + 1 < x; }   // WRONG: compiler may fold this to `false`
```

Check *before* the operation instead: `x == std::numeric_limits<int>::max()`, or use compiler builtins like
`__builtin_add_overflow` (GCC/Clang) — and in C++26, `<stdckdint.h>`'s `ckd_add` is coming from C23.

## Casts: say what you mean

C++ has named casts so each one is searchable and limited:

| Cast | Use for |
|---|---|
| `static_cast<T>(x)` | Normal, checked-at-compile-time conversions (`double`→`int`, base→derived pointers you know are right) |
| `const_cast<T>(x)` | Removing `const` (rarely legitimate) |
| `reinterpret_cast<T>(x)` | Reinterpreting bits/pointers (low-level, dangerous) |
| `dynamic_cast<T>(x)` | Checked downcasts in class hierarchies (Week 6) |

Avoid C-style `(int)x` casts — they silently pick the most dangerous cast that works.

## Order of evaluation

In `f(a(), b())`, the order in which `a()` and `b()` run is unspecified. C++17 *did* fix some cases:
in `a << b`, `a = b`, `a[b]` and `a.b`, the left side is now evaluated first. So `std::cout << i++ << i;`
is defined since C++17 (but still confusing — don't write it).

!!! warning "Common pitfall"
    Turn on `-Wconversion -Wsign-conversion` for code that does a lot of arithmetic (DSP, codecs).
    They are noisy at first, but they catch exactly the bugs in this lesson.

## Key takeaways

!!! success "Key takeaways"
    - Small integer types are promoted to `int` before arithmetic.
    - Mixing signed and unsigned converts the signed value to unsigned — use `std::cmp_less` & co. (C++20).
    - Signed overflow is UB (the optimizer exploits it); unsigned wraps.
    - Use named casts (`static_cast`), never C-style casts.
    - C++17 fixed evaluation order for `<<`, `=`, `[]`, but function-argument order is still unspecified.

## Quiz

**Q1.** Why is `x + 1 < x` a bad overflow check for `int x`?

??? question "Show answer"
    Signed overflow is undefined behaviour, so the compiler may assume it never happens and simplify the expression to `false`. Check against `INT_MAX` before adding instead.

**Q2.** What type and value does `std::uint8_t{250} + std::uint8_t{10}` have?

??? question "Show answer"
    `int` with value 260, because of integer promotion.

**Q3.** What does `std::cmp_less(-1, 0u)` return?

??? question "Show answer"
    `true`. It compares mathematical values regardless of signedness.

**Q4.** Which cast would you use to convert a `double` to an `int` deliberately?

??? question "Show answer"
    `static_cast<int>(d)`.

## Practice lab (optional)

Write `int clamp_add(int a, int b)` that returns `a + b`, but saturates at `INT_MAX`/`INT_MIN` instead of
overflowing — without ever performing an overflowing signed addition.

??? tip "Full solution"
    ```cpp title="examples/week01/lesson05_lab_solution.cpp"
    --8<-- "examples/week01/lesson05_lab_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week01/lesson05_lab_solution.out"
    ```

