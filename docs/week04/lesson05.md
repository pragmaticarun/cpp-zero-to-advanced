# Lesson 4.5: Operator overloading and the spaceship operator <=>

<span class="stdtag">C++23</span> · about 12 minutes

## Why this matters

Suppose you have a `Version{major, minor, patch}` and want to sort a list of them, or check
`if (v >= Version{2, 1, 0})`. Before C++20 that meant writing six comparison operators by hand, carefully
keeping them consistent. Now it's one line. Operator overloading lets your types feel like built-in ones —
let's see how to do it well, and what *not* to do.

## The basic idea

An operator is just a function with a special name: `a + b` calls `operator+(a, b)` (or `a.operator+(b)`).
The rules of thumb, from the C++ Core Guidelines and decades of experience:

- **Do what the built-in operator would do.** `+` adds, `==` compares. No clever surprises.
- **Binary operators that treat both sides symmetrically should be non-members** (often `friend`s),
  so conversions apply to both operands.
- **Implement `+` in terms of `+=`.**

## Comparisons in C++20: `<=>` and `= default`

```cpp
struct Version {
    int major, minor, patch;
    auto operator<=>(const Version&) const = default;   // gives <, <=, >, >=
    bool operator==(const Version&) const = default;    // gives ==, != (implied by <=> = default too)
};
```

That defaulted `<=>` compares members in declaration order (lexicographically), exactly what you want for
versions. The result is a *comparison category*:

| Category | Meaning | Example |
|---|---|---|
| `std::strong_ordering` | equal values are indistinguishable | `int` |
| `std::weak_ordering` | equivalent values may differ | case-insensitive strings |
| `std::partial_ordering` | some values are unordered | `double` (NaN) |

C++20 also *rewrites* expressions: `a != b` becomes `!(a == b)`, and `a < b` can use `(a <=> b) < 0`,
including with the arguments reversed. So you write two functions and get all six operators.

```cpp title="examples/week04/lesson05.cpp"
--8<-- "examples/week04/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week04/lesson05.out"
```

## Arithmetic operators

The canonical pattern, shown for a 2D vector in the example: a member `operator+=` that modifies `*this`
and returns `*this` by reference, and a non-member `operator+` that takes its left operand **by value**,
uses `+=`, and returns it.

## Other operators you'll overload

- `operator[]` for containers. C++23 allows multiple arguments: `m[i, j]`.
- `operator()` makes a *function object* (functor) — the idea behind lambdas.
- `operator<<` with `std::ostream` for printing.

## The wrong way: surprising operators

```cpp
Matrix operator*(const Matrix&, const Matrix&);   // fine: math
Logger& operator<<(Logger&, Level);               // fine: established stream idiom
bool operator&&(const A&, const B&);              // AVOID: loses short-circuit evaluation
Thing& operator,(Thing&, Thing&);                 // AVOID: nobody expects this
```

Overloaded `&&`, `||` and `,` don't short-circuit / sequence the way the built-ins do. Don't overload them.

## Key takeaways

!!! success "Key takeaways"
    - Overload operators only with their conventional meaning.
    - In C++20, `auto operator<=>(const T&) const = default;` gives all six comparisons, member-wise.
    - Comparison categories: strong, weak, partial ordering.
    - Implement `+` via `+=`; make symmetric binary operators non-members.
    - Never overload `&&`, `||` or `,`.

## Quiz

**Q1.** With only `bool operator==(const T&) const` defined, does `a != b` compile in C++20?

??? question "Show answer"
    Yes. C++20 rewrites `a != b` as `!(a == b)`.

**Q2.** What comparison category does `double <=> double` return and why?

??? question "Show answer"
    `std::partial_ordering`, because NaN is unordered with respect to every value.

**Q3.** Why take the left operand of `operator+` by value?

??? question "Show answer"
    We need a copy to modify anyway; taking it by value lets the compiler move from temporaries and makes the implementation `return a += b;`.

**Q4.** Why shouldn't you overload `operator&&`?

??? question "Show answer"
    The overloaded version is a normal function call: both operands are always evaluated, so short-circuiting is lost.

