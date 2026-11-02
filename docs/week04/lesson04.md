# Lesson 4.4: explicit, conversions, static members, friends, nested classes

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

Here's a real surprise: `void play(Duration d);` ... `play(5);` compiles, and plays for 5 *what*? If
`Duration` has a constructor taking an `int`, C++ will quietly convert. Implicit conversions are
sometimes great (`std::string s = "hi";`) and sometimes a bug factory. This lesson is about controlling
them, plus a few other class features you'll meet constantly.

## `explicit`: no surprise conversions

A constructor that can be called with one argument is a *converting constructor*: the compiler may use it
implicitly. Mark it `explicit` unless the conversion is truly natural and lossless.

```cpp
struct Millis { explicit Millis(long v) : value{v} {} long value; };
void sleep_for(Millis);
sleep_for(5);           // ERROR (good!) — what unit is 5?
sleep_for(Millis{5});   // clear
```

C++20 added `explicit(condition)` for generic code, e.g. "explicit only if the conversion is narrowing".

## Conversion operators

The reverse direction: `operator T() const` lets your type convert *to* `T`. The most common one is
`explicit operator bool()` — it works in `if (x)` and `!x` (contextual conversion) but won't let your
object silently become `1` in arithmetic.

## `static` members: belong to the class, not an object

A `static` data member has one instance shared by all objects; a `static` member function has no `this`.
Since C++17 you can define it inline: `inline static int count = 0;`.

## `friend`

A `friend` declaration grants a function or class access to private members. It's not a hack — it's the
right tool for operators that are naturally non-members (like `operator<<`) and for tightly coupled
helper classes. Keep friends few and close.

## Nested and local classes

A class defined inside another (`Playlist::Iterator`) is a *nested class*: it's scoped by the outer class
and can access its private members. A class defined inside a function is a *local class* — handy for
one-off helpers, though lambdas usually do the job.

```cpp title="examples/week04/lesson04.cpp"
--8<-- "examples/week04/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week04/lesson04.out"
```

!!! warning "Common pitfall: implicit `operator bool`"
    Pre-C++11 code used `operator void*()` or non-explicit `operator bool()` hacks, which allowed
    nonsense like `stream1 + stream2`. Always write `explicit operator bool() const`.

## Key takeaways

!!! success "Key takeaways"
    - Mark single-argument constructors `explicit` unless the conversion is obviously safe.
    - Write `explicit operator bool()`; it still works in `if` and `!`.
    - `static` members belong to the class; `inline static` (C++17) defines them in the class body.
    - `friend` is the normal way to write non-member operators that need private access.

## Quiz

**Q1.** Why does `if (codec)` compile with an `explicit operator bool`, but `int n = codec;` doesn't?

??? question "Show answer"
    `if` performs a *contextual conversion* to bool, which is allowed to use explicit conversion operators. Copy-initialization of `int` would need an implicit conversion.

**Q2.** Does a `static` member function have a `this` pointer?

??? question "Show answer"
    No; it isn't called on an object. It can access only static members (or objects passed to it).

**Q3.** When is `friend` appropriate?

??? question "Show answer"
    For non-member functions that are part of a class's interface and need private access (e.g. `operator<<`, symmetric binary operators), or tightly coupled helper classes.

