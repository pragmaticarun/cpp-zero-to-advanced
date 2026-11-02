# Lesson 1.4: Variables and initialization: auto, const, constexpr

<span class="stdtag">C++20</span> · about 10 minutes

## Why this matters

Here's a bug that has shipped in real products: `int volume; if (muted) volume = 0; play(volume);`. When
not muted, `volume` is *uninitialized* — reading it is undefined behaviour. C++ won't stop you, so you
need habits that make the mistake impossible. This lesson is about those habits.

## Always initialize

A local variable of fundamental type without an initializer has an *indeterminate* value. Reading it is
undefined behaviour (UB) — the program may print garbage, or the optimizer may do something truly strange.

```cpp
int x;            // WRONG (if you read it before assigning)
int y = 0;        // OK
```

## Three ways to initialize (and which to prefer)

```cpp
int a = 3;      // copy-initialization
int b(3);       // direct-initialization
int c{3};       // list-initialization (brace init), C++11
```

All three give 3 here. The braces have one superpower: **they reject narrowing conversions**.

```cpp
double ratio = 2.7;
int n1 = ratio;   // compiles, silently truncates to 2 (warning with -Wconversion)
int n2{ratio};    // ERROR: narrowing conversion from double to int
```

That's why many style guides say "prefer `{}`". There are a few pitfalls with braces and constructors
that take `std::initializer_list` (we'll meet them in Week 4), but for plain variables, braces are a great
default.

## `auto`: let the compiler figure out the type

`auto` deduces the type from the initializer:

```cpp
auto count = 10;        // int
auto ratio = 0.5;       // double
auto name = std::string{"Ada"};  // std::string
```

Use `auto` when the type is obvious from the right-hand side or long and noisy (iterators). It also
*forces* you to initialize — `auto x;` doesn't compile. One gotcha: `auto` drops top-level `const` and
references; we'll see that in Lesson 2.3.

## `const` and `constexpr`

- `const` means "I won't modify this after initialization." The value may be computed at run time.
- `constexpr` means "this is known at compile time" — the compiler must be able to evaluate it.

```cpp title="examples/week01/lesson04.cpp"
--8<-- "examples/week01/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week01/lesson04.out"
```

`constexpr` values can be used where the language needs a compile-time constant, like array sizes and
template arguments. We'll go much deeper (constexpr functions, `consteval`, `constinit`) in Week 8.

!!! tip "Pro tip: make const the default"
    Mark everything `const` that doesn't need to change. It documents intent, prevents accidents, and
    makes code easier to reason about. Many experienced C++ programmers find most of their local
    variables end up `const`.

## `decltype`: the type of an expression

`decltype(expr)` gives you the declared type of an expression without evaluating it. You'll mostly see it
in generic code, e.g. `decltype(a + b)`. Don't worry about it much yet.

## Key takeaways

!!! success "Key takeaways"
    - Always initialize variables; reading an uninitialized `int` is undefined behaviour.
    - Brace initialization `{}` rejects narrowing conversions.
    - `auto` deduces from the initializer and forces you to initialize.
    - `const` = won't change; `constexpr` = known at compile time.

## Quiz

**Q1.** Does `int n{3.5};` compile?

??? question "Show answer"
    No. List-initialization forbids narrowing from `double` to `int`. `int n = 3.5;` compiles (truncating to 3), typically with a warning under `-Wconversion`.

**Q2.** What's the difference between `const int a = f();` and `constexpr int b = f();`?

??? question "Show answer"
    `a` can be initialized at run time; it just can't be modified afterwards. `b` requires `f()` to be evaluable at compile time (a `constexpr` function with constant arguments), otherwise it's a compile error.

**Q3.** What type is `auto x = 5u;`?

??? question "Show answer"
    `unsigned int`.

