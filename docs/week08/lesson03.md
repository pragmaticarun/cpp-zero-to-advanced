# Lesson 8.3: Lambdas in depth

<span class="stdtag">C++23</span> · about 11 minutes

## Why this matters

Sorting tracks by duration, filtering sensor readings above a threshold, registering a callback for "new
frame ready" — all need a small function right where you use it. Lambdas are that. And they're not slow:
each lambda is a tiny class the compiler can inline completely.

## Anatomy

```cpp
[captures](params) mutable -> ReturnType { body }
```

A lambda creates an object of a unique, unnamed class with an `operator()`. Captures become its members.

| Capture | Meaning |
|---|---|
| `[x]` | copy `x` |
| `[&x]` | reference to `x` |
| `[=]` / `[&]` | everything used, by copy / by reference |
| `[p = std::move(ptr)]` | init capture (C++14): move-only values, renaming |
| `[this]` / `[*this]` | the object by pointer / by copy (C++17) |

## The wrong way: dangling reference captures

```cpp
std::function<int()> make_counter() {
    int count = 0;
    return [&count] { return ++count; };   // count dies when make_counter returns: UB
}
```

Capturing by reference is fine for lambdas used *immediately* (e.g. passed to `std::sort`). For lambdas
that are *stored* (callbacks, threads), capture by value or init-capture.

```cpp title="examples/week08/lesson03.cpp"
--8<-- "examples/week08/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week08/lesson03.out"
```

## Generic and template lambdas

`[](const auto& a, const auto& b)` is a generic lambda (a template `operator()`). C++20 template lambdas
`[]<typename T>(const std::vector<T>& v)` let you name the type.

## IILE: initialize a const with complex logic

```cpp
const auto config = [&] { Config c; /* many steps */ return c; }();
```

!!! tip "Pro tip"
    `mutable` lets a by-copy lambda modify its own copies. State lives in the lambda object, so copies of
    the lambda have *independent* state.

## Key takeaways

!!! success "Key takeaways"
    - A lambda is an object of an unnamed class; captures are its members.
    - Capture by reference only for lambdas used before the captured variables die.
    - Init captures move in move-only state; `mutable` allows modifying copies.
    - Generic, template, constexpr and (C++23) static lambdas cover most callback needs.

## Quiz

**Q1.** Why is `[&count]` dangerous in a returned lambda?

??? question "Show answer"
    The lambda outlives `count`, a local variable; calling it later reads a dangling reference (UB).

**Q2.** Why did `copy()` print 1 while `counter` printed 1 then 2?

??? question "Show answer"
    `copy` was copied from `counter` before it was called, so it has its own independent `n`.

**Q3.** How do you capture a `std::unique_ptr` into a lambda?

??? question "Show answer"
    With an init capture: `[p = std::move(ptr)] { ... }`.

