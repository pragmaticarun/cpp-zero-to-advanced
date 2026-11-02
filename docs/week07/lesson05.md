# Lesson 7.5: Type traits, if constexpr, and SFINAE

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

Sometimes a generic function must do different things for different types: serialize integers as
big-endian bytes, floats as IEEE bits, strings as length + characters. `<type_traits>` lets you *ask
questions about types* at compile time, and `if constexpr` lets you branch on the answers — with the
discarded branch never even compiled.

## Asking questions about types

```cpp
std::is_integral_v<T>            // true for int, char, bool...
std::is_trivially_copyable_v<T>  // safe to memcpy?
std::is_same_v<T, U>
std::remove_cvref_t<T>           // strip const, volatile and references (C++20)
std::conditional_t<B, X, Y>      // pick a type
```

`_v` gives a value, `_t` gives a type.

## `if constexpr` (C++17)

```cpp
if constexpr (std::is_integral_v<T>) { ... }   // other branch is discarded at compile time
```

With plain `if`, *both* branches must compile for every `T`. With `if constexpr`, the discarded branch
isn't instantiated — so it may contain code that's invalid for this `T`.

```cpp title="examples/week07/lesson05.cpp"
--8<-- "examples/week07/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week07/lesson05.out"
```

## SFINAE: the old way to constrain templates

"Substitution Failure Is Not An Error": if substituting `T` into a template's *signature* fails, that
overload is silently removed instead of causing an error. Pre-C++20 code used this with `std::enable_if`:

```cpp
template <typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
void encode(T value);
```

And the **detection idiom** with `std::void_t` checks whether an expression is valid ("does `T` have a
`.size()`?"). It works, but it's cryptic. In C++20, **concepts** (next week) replace almost all of it. You
need to *read* SFINAE; you rarely need to write it any more.

!!! tip "Pro tip: `static_assert` your assumptions"
    `static_assert(std::is_trivially_copyable_v<Header>);` next to a `memcpy` turns a silent future bug into
    a compile error.

## Key takeaways

!!! success "Key takeaways"
    - Type traits answer questions (`is_integral_v`) and transform types (`remove_cvref_t`) at compile time.
    - `if constexpr` discards the untaken branch, so it can contain code invalid for that type.
    - SFINAE/`enable_if`/`void_t` are the pre-C++20 constraint tools — read them, prefer concepts for new code.
    - `static_assert` documents and enforces type assumptions.

## Quiz

**Q1.** Why can't a plain `if` replace `if constexpr` in `encode`?

??? question "Show answer"
    Both branches of a plain `if` must compile for every `T`; e.g. `value >> 8` doesn't compile for `std::string`.

**Q2.** Why does `static_assert(sizeof(U) == 0, ...)` not fire for supported types?

??? question "Show answer"
    It's in a discarded `if constexpr` branch of a template and depends on `U`, so it's only evaluated when that branch is instantiated.

**Q3.** What does SFINAE stand for and what does it do?

??? question "Show answer"
    Substitution Failure Is Not An Error: when substituting template arguments into a signature fails, that candidate is dropped from overload resolution instead of causing a hard error.

