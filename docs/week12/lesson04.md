# Lesson 12.4: Text: std::format, std::print, iostreams, charconv, and Unicode

<span class="stdtag">C++23</span> · about 13 minutes

## Why this matters

Printing a table of meter readings with aligned columns used to mean either `printf` (fast, type-unsafe) or
iostreams (type-safe, verbose, slow, stateful). C++20's `std::format` and C++23's `std::print` give you
Python-style formatting that's type-safe, checked at compile time, and fast. We'll also cover the
fastest number parsing in the library (`from_chars`) and the state of Unicode.

## `std::format` and `std::print`

```cpp
std::println("{:<10} {:>8.2f} dB", name, level);    // left-align 10, right-align 8 with 2 decimals
```

Format spec mini-language: `{index:fill align sign # 0 width .precision type}`. Examples: `{:08.3f}`, `{:#x}`,
`{:^20}`, `{:+}`. The format string is checked **at compile time**: a mismatch like `{:d}` with a string is a
compile error. For runtime format strings use `std::vformat` / `std::runtime_format` (C++26).

C++23 formats ranges too: `std::println("{}", vec)` prints `[1, 2, 3]`.

## Custom types

Specialize `std::formatter<T>`: implement `parse` (or inherit from an existing formatter) and `format`.

```cpp title="examples/week12/lesson04.cpp"
--8<-- "examples/week12/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week12/lesson04.out"
```

## iostreams: still everywhere

You'll still use `std::cout`, `std::ifstream` and `std::stringstream`. Know their pitfalls: manipulators
like `std::hex` and `std::setprecision` are *sticky* (they stay set), `std::endl` flushes (slow in loops —
use `'\n'`), and `std::ios::sync_with_stdio(false)` speeds up console I/O when you don't mix with C stdio.

## `from_chars` / `to_chars`

Locale-independent, non-allocating, non-throwing, and the fastest conversions available. Always check the
returned `ec` *and* the end pointer.

## Unicode: the honest version

`std::string` holds bytes; it doesn't know about characters. `u8"..."` literals are `char8_t` (C++20),
which doesn't convert implicitly to `char`. `size()` counts bytes, not characters. For real text processing
(normalization, case folding, grapheme clusters) use a library such as ICU. `std::print` writes UTF-8
correctly to Unicode-capable terminals, which iostreams on Windows historically did not.

## Key takeaways

!!! success "Key takeaways"
    - `std::format`/`std::println` give type-safe, compile-time-checked, Python-style formatting.
    - Specialize `std::formatter<T>` (often by inheriting an existing one) for your types.
    - iostream manipulators are sticky; prefer `'\n'` over `std::endl` in loops.
    - `from_chars`/`to_chars` are the fastest, locale-free conversions; `std::string` is bytes, not characters.

## Quiz

**Q1.** What happens if you write `std::format("{:d}", std::string{"x"})`?

??? question "Show answer"
    A compile-time error: the format string is checked against the argument types.

**Q2.** Why can `std::endl` make output slow?

??? question "Show answer"
    It flushes the stream every time; in a loop that defeats buffering.

**Q3.** How many bytes does `u8"é"` (one character, U+00E9) use, excluding the terminator?

??? question "Show answer"
    Two bytes in UTF-8.

