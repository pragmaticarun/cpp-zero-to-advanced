# Lesson 12.7: A tour of the rest: random, regex, math, bits, limits, and more

<span class="stdtag">C++23</span> · about 12 minutes

## Why this matters

The standard library has many smaller headers that each solve one problem well — and a couple that are
famously slow or awkward. This lesson is a guided tour: what each is for, the idiomatic call, and the one
pitfall to remember.

## `<random>`: never `rand()`

```cpp
std::mt19937 rng{std::random_device{}()};          // engine, seeded
std::uniform_int_distribution<int> die{1, 6};      // distribution
int roll = die(rng);
```

`rand() % 6` is biased and low quality. Engines are deterministic given a seed (great for reproducible
tests); distributions shape the output. Note: *distributions* are not guaranteed to produce identical
sequences across standard library implementations — only engines are.

## `<regex>`: correct but slow

`std::regex` works, but common implementations are slow and can blow the stack on long inputs. Fine for
config parsing; for hot paths use a dedicated library (RE2, PCRE2, CTRE) or hand-written parsing.

## Math, constants and limits

`<numbers>` (C++20) gives `std::numbers::pi`, `e`, `sqrt2`... `<cmath>` has `std::hypot`, `std::lerp`
(C++20), special functions (`std::beta`, `std::cyl_bessel_j`). `std::numeric_limits<T>` tells you `max()`,
`lowest()`, `epsilon()`, `infinity()`. Remember: `numeric_limits<float>::min()` is the smallest *positive*
normal value, not the most negative!

## Debugging helpers

`std::source_location::current()` (C++20) gives file, line and function — a macro-free logging helper.
`std::stacktrace` (C++23) captures a call stack (library support varies; GCC needs `-lstdc++exp`), so it's
mentioned but not compiled here.

```cpp title="examples/week12/lesson07.cpp"
--8<-- "examples/week12/lesson07.cpp"
```

**Output**:

```text
--8<-- "examples/week12/lesson07.out"
```

## `std::bitset` and `<locale>`

`std::bitset<N>` is a fixed-size bit array with `count()`, `test()`, and string conversion — handy for flags
and register maps. `<locale>` controls number formatting, character classification and collation; it's
global, stateful and slow, which is why `std::format` and `from_chars` are locale-independent by default.

## Key takeaways

!!! success "Key takeaways"
    - Use `<random>` engines + distributions; never `rand() % n`.
    - `std::regex` is correct but slow; avoid it in hot paths.
    - `<numbers>`, `<cmath>` and `numeric_limits` cover constants, math and type limits (`min()` is positive for floats!).
    - `source_location` replaces `__FILE__`/`__LINE__` macros; `bitset` handles flags.

## Quiz

**Q1.** Why is `rand() % 6` a poor die?

??? question "Show answer"
    `rand()` is low-quality and `%` introduces bias when RAND_MAX+1 isn't a multiple of 6; use `std::uniform_int_distribution` with a good engine.

**Q2.** What is `std::numeric_limits<float>::min()`?

??? question "Show answer"
    The smallest positive normalized float (~1.18e-38), not the most negative value — that's `lowest()`.

**Q3.** Are `std::uniform_int_distribution` results identical across GCC and Clang for the same seed?

??? question "Show answer"
    Not guaranteed — engines are specified exactly, but distribution algorithms are implementation-specific.

