# Lesson 2.5: Enums, structs and attributes

<span class="stdtag">C++23</span> · about 10 minutes

## Why this matters

Here's a function signature from a real codebase: `open_stream(int, int, bool, bool)`. What does
`open_stream(2, 1, true, false)` mean? Nobody knows without reading the docs. Enums and structs let you
give *meaning* to values, and the compiler then checks that meaning for you. Attributes let you tell the
compiler (and readers) even more. Let's make that call readable.

## Old enums leak and convert

```cpp
enum Color { red, green };       // unscoped: `red` is a global name
enum Fruit { apple, orange };
int x = red + apple;             // compiles! nonsense, but legal (and warns)
```

## `enum class`: scoped and strongly typed (C++11)

```cpp
enum class Codec : std::uint8_t { aac, opus, flac };   // explicit underlying type
Codec c = Codec::opus;          // must qualify
// int n = c;                   // ERROR: no implicit conversion
auto n = std::to_underlying(c); // C++23; or static_cast<std::uint8_t>(c)
```

Always prefer `enum class`. In C++20, `using enum Codec;` inside a `switch` saves you typing
`Codec::` on every case.

## Structs group data

```cpp
struct StreamConfig {
    Codec codec = Codec::aac;   // default member initializers (C++11)
    int sample_rate = 48'000;
    int channels = 2;
    bool low_latency = false;
};
```

Now `open_stream(StreamConfig{.codec = Codec::opus, .low_latency = true})` reads like documentation.
(Those `.name =` *designated initializers* are C++20; Week 5 covers them in detail.)

## Attributes

Attributes are annotations in `[[double brackets]]`:

| Attribute | Meaning |
|---|---|
| `[[nodiscard]]` (C++17; with reason C++20) | warn if the caller ignores the return value |
| `[[maybe_unused]]` | silence unused warnings |
| `[[deprecated("use X")]]` (C++14) | warn on use |
| `[[noreturn]]` (C++11) | function never returns (e.g. calls `std::abort`) |
| `[[fallthrough]]` (C++17) | intentional switch fallthrough |
| `[[likely]]` / `[[unlikely]]` (C++20) | branch hints for the optimizer |
| `[[no_unique_address]]` (C++20) | an empty member may take no space |
| `[[assume(expr)]]` (C++23) | the optimizer may assume `expr` is true — UB if it isn't! |

```cpp title="examples/week02/lesson05.cpp"
--8<-- "examples/week02/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week02/lesson05.out"
```

`[[nodiscard]]` is the one to adopt immediately. Put it on functions where ignoring the result is almost
certainly a bug: error codes, `empty()`-style queries, factory functions.

!!! warning "Be careful with `[[likely]]` and `[[assume]]`"
    Measure before adding branch hints; the compiler and CPU predictor are usually good already.
    `[[assume]]` is a promise: if it's ever false, you have undefined behaviour.

## Key takeaways

!!! success "Key takeaways"
    - Prefer `enum class` (scoped, no implicit conversions, explicit underlying type).
    - Use structs with default member initializers to replace long lists of `int`/`bool` parameters.
    - `[[nodiscard]]` turns ignored error results into compiler warnings — use it generously.
    - `[[assume]]` and `[[likely]]` are optimization hints; `[[assume]]` is UB if false.

## Quiz

**Q1.** Name two problems with unscoped enums that `enum class` fixes.

??? question "Show answer"
    Unscoped enumerators leak into the enclosing scope (name clashes), and they implicitly convert to `int` (allowing nonsense arithmetic/comparisons between unrelated enums).

**Q2.** How do you get the integer value of an `enum class` in C++23?

??? question "Show answer"
    `std::to_underlying(e)` from `<utility>` (or `static_cast<std::underlying_type_t<E>>(e)` before C++23).

**Q3.** What happens if the condition in `[[assume(x > 0)]]` is false at run time?

??? question "Show answer"
    Undefined behaviour. The optimizer was allowed to rely on it.

