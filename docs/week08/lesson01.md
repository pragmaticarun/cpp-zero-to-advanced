# Lesson 8.1: Concepts and requires-clauses

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

Remember the 200-line template error from Week 7? Concepts fix that. A concept is a *named compile-time
predicate on types*: "T is something you can add and divide". Put it on a template and two things happen:
callers get a one-line error that says which requirement failed, and you can overload templates on
capabilities cleanly — no SFINAE tricks.

## Using standard concepts

```cpp
#include <concepts>
template <std::integral T> T gcd(T a, T b);
void log_count(std::unsigned_integral auto n);         // constrained auto
```

`<concepts>` provides `std::integral`, `std::floating_point`, `std::same_as`, `std::convertible_to`,
`std::totally_ordered`, `std::invocable`, `std::regular`, ...; `<iterator>` and `<ranges>` add
`std::input_iterator`, `std::ranges::range`, `std::ranges::random_access_range`, and more.

## Writing your own

```cpp
template <typename T>
concept Averageable = requires(T a, T b, std::size_t n) {
    { a + b } -> std::convertible_to<T>;     // expression must compile, result convertible
    { a / n } -> std::convertible_to<T>;
    T{};                                     // default constructible
};
```

A `requires`-expression lists expressions that must be valid. It doesn't evaluate them.

## The payoff: better errors

Call a constrained template with a wrong type and the compiler says "constraints not satisfied" and names
the failed requirement — instead of an error buried deep inside the body.

```cpp title="examples/week08/lesson01.cpp"
--8<-- "examples/week08/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week08/lesson01.out"
```

## Overloading by constraints

If two overloads both match, the **more constrained** one wins (if one's constraints *subsume* the other's).
That's how the example picks a faster `advance_by` for random-access iterators. Subsumption only works
through named concepts — not through arbitrary boolean expressions — another reason to name your concepts.

!!! tip "Pro tip"
    Constrain on *what you use*, not on what you think the type "is". `requires { a + b }` is better than
    "must be a number" if all you do is add.

## Key takeaways

!!! success "Key takeaways"
    - A concept is a named compile-time predicate; constrain templates with it.
    - `requires` expressions list operations that must compile, optionally with result constraints.
    - Constrained templates produce short, specific errors.
    - When overloads both match, the more constrained one (by subsumption of named concepts) wins.

## Quiz

**Q1.** What does `{ a + b } -> std::convertible_to<T>;` require?

??? question "Show answer"
    That `a + b` is a valid expression and its result type is convertible to `T`.

**Q2.** Why did `advance_by` on a `std::vector` iterator choose the "jump" version?

??? question "Show answer"
    Both overloads match, but `std::random_access_iterator` subsumes `std::input_iterator`, so the more constrained overload wins.

**Q3.** Does a `requires`-expression evaluate its expressions at run time?

??? question "Show answer"
    No — they're unevaluated operands; only their validity is checked at compile time.

