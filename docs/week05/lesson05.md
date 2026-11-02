# Lesson 5.5: Aggregates, designated initializers, structured bindings, user-defined literals

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

Not every type needs constructors and private members. A lot of real code is just *data*: a config, a
point, a parsed header. C++ has a lightweight path for those types — aggregates — and C++17/20 made them
really pleasant to use: name the fields when creating them, unpack them by name when reading them. Let's
look at the modern toolbox for "plain data".

## Aggregates

An **aggregate** is (roughly) an array or a class with no user-declared constructors, no private/protected
non-static data members, no virtual functions, and no virtual/private bases. You initialize it with braces
listing the members in order:

```cpp
struct Rgb { std::uint8_t r, g, b; };
Rgb red{255, 0, 0};
```

## Designated initializers (C++20)

Naming the members makes the call site self-documenting:

```cpp
EncoderConfig cfg{.bitrate = 128'000, .vbr = true};   // others get their default member initializers
```

Rules (stricter than C): designators must appear in **declaration order**, and you can't mix designated
and positional elements. C++20 also allows aggregate init with parentheses, `Rgb red(255, 0, 0);`, which
helps generic code like `std::make_unique<Rgb>(255, 0, 0)`.

## Structured bindings (C++17)

The reverse: unpack an aggregate, `std::pair`, `std::tuple` or array into named variables:

```cpp
for (const auto& [name, rate] : rates) ...       // map iteration, finally readable
auto [it, inserted] = set.insert(42);
```

The names are aliases into a hidden object, so `auto&` binds them by reference to the original. Your own
non-aggregate types can opt in by implementing the *tuple protocol* (`std::tuple_size`,
`std::tuple_element`, `get<I>`) — shown in the example.

## User-defined literals (C++11)

You've used standard ones: `"abc"s` (string), `"abc"sv`, `100ms` (chrono), `2.0i` (complex). You can
define your own with `operator""_suffix`; user suffixes must start with an underscore:

```cpp
constexpr Hertz operator""_kHz(unsigned long long v) { return Hertz{v * 1000}; }
auto rate = 48_kHz;
```

They're great for units: `48_kHz` can't be mixed up with `48`.

```cpp title="examples/week05/lesson05.cpp"
--8<-- "examples/week05/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week05/lesson05.out"
```

!!! warning "Common pitfall: adding a constructor removes aggregate-ness"
    The moment you add *any* user-declared constructor (even `= default` since C++20), a struct stops being
    an aggregate and designated initializers stop compiling. Use default member initializers instead.

## Key takeaways

!!! success "Key takeaways"
    - Aggregates are plain data types initialized member-wise with braces.
    - C++20 designated initializers name fields at the call site (in declaration order).
    - Structured bindings unpack pairs, tuples, arrays, aggregates — and your types via the tuple protocol.
    - User-defined literals (`48_kHz`) make units explicit.

## Quiz

**Q1.** Does `struct P { int x, y; }; P p{.y = 1, .x = 2};` compile in C++20?

??? question "Show answer"
    No — designators must appear in declaration order (`.x` before `.y`).

**Q2.** In `for (auto& [k, v] : m)` over a `std::map`, can you modify `k`?

??? question "Show answer"
    No: map elements are `std::pair<const Key, T>`, so `k` refers to a const key. You can modify `v`.

**Q3.** Why must user-defined literal suffixes start with `_`?

??? question "Show answer"
    Suffixes without an underscore are reserved for the standard library (like `s`, `ms`, `sv`).

