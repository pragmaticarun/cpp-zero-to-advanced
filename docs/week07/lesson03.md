# Lesson 7.3: Non-type parameters, variadic templates, and fold expressions

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

How does `std::make_unique` accept *any* number of constructor arguments? How does `std::format` take any
number of values? The answer is **variadic templates** — templates that take packs of types. Combined with
fold expressions, they let you write "do this for every argument" in a single line.

## Non-type template parameters

Template parameters can be values, not just types: `std::array<int, 8>` takes the size `8`.
Allowed: integers, enums, pointers, `auto` (C++17), and since C++20 floating-point and *structural* class
types (all public, non-mutable members) — so you can even pass a small string literal wrapper.

## Parameter packs

```cpp
template <typename... Args>          // a pack of types
void log(const Args&... args);       // a pack of function parameters
sizeof...(Args)                      // how many
```

## Fold expressions (C++17)

Fold over a binary operator:

| Fold | Expands to |
|---|---|
| `(args + ...)` | `a1 + (a2 + (a3))` |
| `(... + args)` | `((a1) + a2) + a3` |
| `(init + ... + args)` | with an initial value — safe for empty packs |
| `((std::cout << args), ...)` | comma fold: "do this for each" |

```cpp title="examples/week07/lesson03.cpp"
--8<-- "examples/week07/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week07/lesson03.out"
```

## The old way: recursion

Before C++17 you'd write a base case and a recursive case peeling off one argument at a time. You'll see
it in older code; folds and `if constexpr` replace most of it.

!!! tip "Pro tip"
    Use `std::forward<Args>(args)...` to pass a pack along unchanged — that's perfect forwarding, the next
    lesson.

## Key takeaways

!!! success "Key takeaways"
    - Templates can take values (NTTPs), including `auto` and, in C++20, structural class types.
    - `typename... Args` declares a pack; `sizeof...` counts it; `args...` expands it.
    - Fold expressions apply an operator across a pack; the comma fold means 'for each'.
    - Use an initial value in folds when the pack may be empty.

## Quiz

**Q1.** What does `(0 + ... + args)` evaluate to with no arguments?

??? question "Show answer"
    `0` — the initial value; without it, an empty `+` fold is ill-formed.

**Q2.** How do you count the elements of a parameter pack?

??? question "Show answer"
    `sizeof...(Args)` (or `sizeof...(args)`).

**Q3.** Since C++20, what kinds of class types can be NTTPs?

??? question "Show answer"
    Structural types: literal class types whose bases and non-static members are all public and non-mutable (and themselves structural).

