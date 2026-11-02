# Lesson 7.1: Function templates and argument deduction

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

You've written `clamp` for `int`. Now you need it for `float`, `double`, and `std::chrono::milliseconds`.
Copy-pasting four versions is how bugs multiply. A function template is a recipe: the compiler stamps out a
real function for each type you use — and each one is as fast as if you'd written it by hand.

## The recipe

```cpp
template <typename T>
T clamp_to(T v, T lo, T hi) { return v < lo ? lo : (hi < v ? hi : v); }

clamp_to(15, 0, 10);        // T deduced as int
clamp_to(0.7, 0.0, 1.0);    // T deduced as double
```

The compiler **deduces** `T` from the arguments, then **instantiates** `clamp_to<int>` — real machine code,
no runtime dispatch.

## The wrong way: conflicting deductions

```cpp
clamp_to(0.7, 0, 1);   // error: T deduced as double AND int
```

Deduction doesn't do conversions. Fix it by making the arguments agree (`0.0, 1.0`), or by specifying
`T` explicitly: `clamp_to<double>(0.7, 0, 1)`.

```cpp title="examples/week07/lesson01.cpp"
--8<-- "examples/week07/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week07/lesson01.out"
```

## Abbreviated templates (C++20)

`auto` in a parameter list makes a function a template:

```cpp
void print_all(const auto& container);   // same as template <typename C> void print_all(const C&)
```

## Templates live in headers

A template isn't code until it's instantiated, and the compiler needs the *definition* to instantiate it.
So templates normally go entirely in headers. (Explicit instantiation and modules — Week 15 — are the
exceptions.)

## `typename` for dependent names

Inside a template, `T::value_type` could be a type or a static member; the compiler assumes *value* unless
you say `typename T::value_type`. Since C++20 many contexts no longer need it, but you'll see it everywhere.

!!! tip "Reading template errors"
    Scroll to the **first** error, then find the line in *your* code ("required from here"). The library
    internals in the middle are rarely the problem.

## Key takeaways

!!! success "Key takeaways"
    - A function template is a recipe; each set of deduced types instantiates a real function.
    - Deduction requires arguments to agree; no implicit conversions during deduction.
    - `auto` parameters (C++20) create abbreviated templates.
    - Template definitions usually live in headers; read errors from the first one, looking for your code.

## Quiz

**Q1.** Why does `clamp_to(0.7, 0, 1)` fail?

??? question "Show answer"
    `T` is deduced as `double` from the first argument and `int` from the others; deduction fails because they conflict.

**Q2.** Do templates have a runtime cost compared to hand-written overloads?

??? question "Show answer"
    No — instantiations are ordinary functions. The costs are compile time and code size.

**Q3.** Why are templates usually defined in headers?

??? question "Show answer"
    The compiler needs the full definition at the point of instantiation in each translation unit.

