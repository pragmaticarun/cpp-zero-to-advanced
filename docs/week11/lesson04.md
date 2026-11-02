# Lesson 11.4: Utilities: pair, tuple, apply, function objects, and friends

<span class="stdtag">C++23</span> · about 10 minutes

## Why this matters

The `<utility>`, `<tuple>` and `<functional>` headers are full of small tools that remove boilerplate:
returning several values, calling a function with arguments stored in a tuple, flipping a predicate,
resetting a member while returning its old value. Individually tiny; together they make code noticeably
cleaner.

## Pairs and tuples

`std::tuple<int, std::string, double>` groups values without naming a struct. Access with `std::get<0>(t)` or
`std::get<std::string>(t)` (if the type is unique) — or, better, structured bindings. Honest advice: if the
tuple escapes a small scope, a named `struct` with named fields is clearer.

`std::tie(a, b) = f();` assigns into existing variables; `std::tie(x.a, x.b) < std::tie(y.a, y.b)` was the
pre-`<=>` way to write lexicographic comparisons.

## `std::apply`

Calls a function with a tuple's elements as arguments — the bridge between stored arguments and calls (used
by thread pools and deferred tasks).

```cpp title="examples/week11/lesson04.cpp"
--8<-- "examples/week11/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week11/lesson04.out"
```

## Function objects

`std::plus<>`, `std::less<>`, `std::greater<>` (the `<>` forms are transparent and generic). C++20 adds
`std::ranges::less` (concept-constrained) and `std::identity` (the default projection). `std::not_fn(pred)`
negates a predicate.

## Small helpers

- `std::exchange(x, new)` — set and return the old value: perfect for move constructors.
- `std::as_const(x)` — get a const reference (call const overloads).
- `std::to_underlying(e)` (C++23) — enum to its underlying integer.
- `std::ref(x)` — pass by reference through APIs that copy (like `std::thread` or `std::bind`).

## Key takeaways

!!! success "Key takeaways"
    - Use tuples locally and structured bindings to unpack; prefer named structs for public APIs.
    - `std::apply` calls a function with a tuple's elements; `make_from_tuple` constructs an object.
    - Transparent function objects (`std::less<>`) and `std::not_fn` replace small lambdas.
    - `std::exchange`, `std::as_const`, `std::to_underlying` and `std::ref` remove common boilerplate.

## Quiz

**Q1.** What does `std::exchange(x, 0)` return?

??? question "Show answer"
    The old value of `x`; `x` is set to 0.

**Q2.** Why is `std::ref(n)` needed in `std::bind_front(bump, std::ref(n))`?

??? question "Show answer"
    `bind_front` stores copies of its arguments; `std::ref` stores a reference wrapper so `bump` modifies the original `n`.

**Q3.** When does `std::get<std::string>(t)` fail to compile?

??? question "Show answer"
    When the tuple has zero or more than one element of type `std::string`.

