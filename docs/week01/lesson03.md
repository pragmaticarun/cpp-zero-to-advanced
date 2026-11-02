# Lesson 1.3: Fundamental types, literals, and fixed-width integers

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

Suppose you're decoding an audio stream: 16-bit signed samples, a 32-bit sample-rate field, an 8-bit
channel count. If you pick `int` for everything and the code runs on a platform where `int` isn't the
size you assumed, the file is garbage. C++ gives you precise control over representation — but you
have to know what the types actually guarantee. Let's look.

## The basic types

| Type | Typical size (64-bit Linux/Android) | Guaranteed by the standard |
|---|---|---|
| `bool` | 1 byte | holds `true`/`false` |
| `char` | 1 byte | `sizeof(char) == 1`; signedness is implementation-defined! |
| `short` | 2 | at least 16 bits |
| `int` | 4 | at least 16 bits |
| `long` | 8 (4 on Windows) | at least 32 bits |
| `long long` | 8 | at least 64 bits |
| `float` / `double` | 4 / 8 | usually IEEE-754 single/double |

Notice "at least". The standard deliberately leaves exact sizes to the platform. On Windows, `long` is
32 bits; on 64-bit Linux it's 64. That has broken plenty of portable code.

## When size matters, say so: `<cstdint>`

For file formats, network protocols and hardware registers, use the fixed-width types:
`std::int8_t`, `std::uint16_t`, `std::int32_t`, `std::uint64_t`. For sizes and indexes use
`std::size_t` (what `sizeof` and `.size()` return).

```cpp title="examples/week01/lesson03.cpp"
--8<-- "examples/week01/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week01/lesson03.out"
```

A few things to notice in that output:

- `std::numeric_limits<T>` (from `<limits>`) tells you a type's range, precision and more at compile time.
- `0.1 + 0.2` is not exactly `0.3`. Floating point stores binary fractions; `0.1` has no exact binary
  representation. Never compare floats with `==` unless you know why it's safe.
- `uint8_t` printed via `std::cout` shows up as a *character* because it's (usually) a typedef for
  `unsigned char`. Cast to `int` to print the number. This one bites every multimedia developer at least once.

## Literals

Literals are how you write values in code:

```cpp
int dec = 255, hex = 0xFF, oct = 0377, bin = 0b1111'1111;  // all 255; ' is a digit separator (C++14)
unsigned u = 42u;  long l = 42L;  long long ll = 42LL;  std::size_t n = 42uz; // uz: C++23
double d = 1.5e3;  float f = 1.5f;
char c = 'A';  char8_t c8 = u8'A';  char16_t c16 = u'A';  char32_t c32 = U'A';
const char* s = "text";  bool b = true;  int* p = nullptr;   // nullptr: C++11
```

`nullptr` (C++11) replaced the old `NULL`/`0` for null pointers — it has its own type, so overloads can't
mistake it for an integer.

## Common mistake: assuming `char` is signed

```cpp
char c = '\xFF';
if (c < 0) { /* true on x86 Linux, FALSE on ARM Linux/Android! */ }
```

On x86, plain `char` is signed; on ARM (most Android devices), it's unsigned. If you mean "a byte", use
`unsigned char`, `std::uint8_t`, or `std::byte` (Week 3).

!!! tip "Pro tip"
    `static_assert(sizeof(Header) == 12);` (Week 9) lets you lock down assumptions about layout at compile
    time, so a port to a new platform fails loudly instead of silently corrupting data.

## Key takeaways

!!! success "Key takeaways"
    - The standard guarantees minimum sizes, not exact ones; `long` differs between Windows and Linux.
    - Use `<cstdint>` fixed-width types for formats/protocols, `std::size_t` for sizes.
    - Floating point is approximate: don't compare with `==` casually.
    - Plain `char` signedness differs between x86 and ARM; use `unsigned char`/`std::byte` for bytes.
    - `uint8_t` prints as a character with iostreams; cast to `int`.

## Quiz

**Q1.** Is `sizeof(long)` always 8 on 64-bit systems?

??? question "Show answer"
    No. It's 8 on 64-bit Linux/macOS/Android (LP64) but 4 on 64-bit Windows (LLP64).

**Q2.** Why does `std::cout << std::uint8_t{65}` print `A`?

??? question "Show answer"
    `std::uint8_t` is typically an alias for `unsigned char`, and the stream prints character types as characters. Cast to `int` first, or use `std::format`/`std::print` (Week 12), which format `unsigned char` as a number.

**Q3.** What's the value of `0b1010'0000`?

??? question "Show answer"
    160 (binary 10100000). The `'` is just a digit separator.

**Q4.** Why prefer `nullptr` over `NULL`?

??? question "Show answer"
    `nullptr` has type `std::nullptr_t` and converts only to pointer types, so overload resolution can't confuse it with an integer like `NULL` (often `0`) could.

