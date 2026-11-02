# Lesson 2.2: Functions, overloading and default arguments

<span class="stdtag">C++20</span> · about 10 minutes

## Why this matters

As soon as a program does more than one thing, you want to name each thing. Functions are names for
behaviour. C++ adds two conveniences you may not have in C: **overloading** (several functions with the
same name but different parameters) and **default arguments**. They're handy — and they have a couple of
sharp corners we'll walk through.

## Anatomy

```cpp
int add(int a, int b) { return a + b; }       // classic
auto add(double a, double b) -> double;        // trailing return type (C++11), same meaning
auto twice(int x) { return 2 * x; }            // return type deduced (C++14): int
```

Most of the time, write the return type explicitly for public functions (it's documentation) and use
deduced `auto` for short local helpers.

## Overloading

You can have several functions with the same name if their parameter lists differ. The compiler picks the
**best match** for each call — that's *overload resolution*. Roughly: an exact match beats a promotion,
which beats a conversion.

```cpp title="examples/week02/lesson02.cpp"
--8<-- "examples/week02/lesson02.cpp"
```

**Output**:

```text
--8<-- "examples/week02/lesson02.out"
```

Notice `describe(2.5f)`: there's no `float` overload, but `float → double` is a *promotion*, which beats
`float → int` (a conversion). And `describe('x')`: `char → int` is a promotion, so it calls `describe(int)`.

## The ambiguous call (the wrong way)

```cpp
void f(long);
void f(double);
f(42);   // ERROR: ambiguous. int->long and int->double are both conversions
```

When this happens, either add an exact overload or make the call explicit (`f(42L)`).

## Default arguments

```cpp
void log(const std::string& msg, int level = 1);
log("hi");        // level = 1
log("oops", 3);
```

Defaults go in the **declaration** (usually the header), not repeated in the definition. They're
substituted at the *call site* — so changing a default in a header requires recompiling the callers, a
subtle point if you ship shared libraries.

!!! warning "Common pitfall: defaults + overloads"
    `void f(int x, int y = 0);` and `void f(int x);` together make `f(1)` ambiguous. Pick one tool.

## Generic functions with `auto` parameters (C++20)

```cpp
auto largest(auto a, auto b) { return a > b ? a : b; }
```

This is an *abbreviated function template*: a template in disguise. We'll unpack templates in Week 7;
for now just know it works for any types that support `>`.

## Key takeaways

!!! success "Key takeaways"
    - Overload resolution prefers exact matches, then promotions, then conversions; ties are errors.
    - Put default arguments in the declaration; they're filled in at the call site.
    - `auto` return types are deduced; `auto` parameters (C++20) make a function template.

## Quiz

**Q1.** Given `void f(int); void f(double);`, which is called by `f('a')`? By `f(1.0f)`?

??? question "Show answer"
    `f(int)` (char→int is an integral promotion) and `f(double)` (float→double is a floating-point promotion).

**Q2.** Why might changing a default argument in a library header not affect an already-compiled app?

??? question "Show answer"
    Defaults are inserted at each call site at compile time, so the app keeps the old value until recompiled.

**Q3.** What does `auto f(auto x)` declare?

??? question "Show answer"
    An abbreviated function template (C++20): equivalent to `template<class T> auto f(T x)`.

