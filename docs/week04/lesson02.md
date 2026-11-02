# Lesson 4.2: Constructors, destructors, and every way to initialize

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

C++ has a famously large number of ways to initialize an object — `T x;`, `T x{};`, `T x();`, `T x = y;`,
`T x(a, b);`, `T x{a, b};` — and some of them do surprisingly different things. This lesson doesn't try to
list every rule. Instead it gives you a small set of habits that are always right, and shows you the three
traps that catch everyone.

## Constructors and the member initializer list

A constructor runs when an object is created. Members should be initialized in the **member initializer
list** (after the `:`), not assigned in the body:

```cpp
class Track {
    std::string title_;
    int length_s_;
public:
    Track(std::string t, int len) : title_{std::move(t)}, length_s_{len} {}   // initialize
    // Track(std::string t, int len) { title_ = t; length_s_ = len; }        // default-construct, then assign
};
```

The second version first default-constructs `title_` and then assigns — wasted work, and impossible for
`const` members, references, or types with no default constructor.

## Default member initializers, delegation, `= default` and `= delete`

```cpp title="examples/week04/lesson02.cpp"
--8<-- "examples/week04/lesson02.cpp"
```

**Output**:

```text
--8<-- "examples/week04/lesson02.out"
```

- **Default member initializers** (`int channels_ = 2;`) give a value whenever a constructor doesn't
  mention that member. They remove a lot of repetition.
- **Delegating constructors** call another constructor of the same class.
- `= default` asks for the compiler-generated version; `= delete` forbids an operation (here: no
  construction from `bool`, which would otherwise convert silently to `int`).
- The **destructor** `~Stream()` runs when the object's lifetime ends. Order: the destructor body runs, then
  members are destroyed in *reverse declaration order*.

!!! warning "A real surprise we hit while writing this lesson"
    Our first draft said `Stream b{"speaker"};` — and it **failed to compile** with "call to deleted
    constructor". Why? A string literal is a `const char*`, and `const char*` → `bool` is a *standard*
    conversion, which beats the *user-defined* conversion `const char*` → `std::string`. So overload
    resolution picked `Stream(bool)`. Without the `= delete`, it would have silently compiled and called the
    wrong constructor. That's precisely why deleting the `bool` overload is a good idea — and why
    `std::string_view` parameters are often friendlier than `std::string` ones.

## Trap 1: members are initialized in declaration order

```cpp
class Buffer {
    std::size_t size_;
    std::vector<int> data_;
public:
    Buffer(std::size_t n) : data_(n), size_(data_.size()) {}  // looks fine...
};
```

This works by luck. But swap the declarations of `size_` and `data_` and `data_(size_)` would read an
uninitialized `size_`. Members are **always** initialized in the order they're *declared*, regardless of the
order in the initializer list. `-Wall` warns (`-Wreorder`) when the orders differ — listen to it.

## Trap 2: braces prefer `std::initializer_list`

```cpp
std::vector<int> a(3, 7);   // three elements: 7 7 7
std::vector<int> b{3, 7};   // two elements: 3 7  (initializer_list constructor wins)
```

If a class has an `initializer_list` constructor, brace-init strongly prefers it. Use parentheses when you
mean "call the size constructor".

## Trap 3: the most vexing parse

```cpp
Stream s();      // NOT an object! Declares a function named s returning Stream.
Stream s{};      // value-initialized object. Use braces.
```

## Habits that are always right

1. Give every member a default member initializer or initialize it in every constructor.
2. Use `T x{...};` for objects, but `( )` when you need a specific non-list constructor of a container.
3. Use `{}` to value-initialize (`int x{};` is 0; `T t{};` runs the default constructor or zero-fills).
4. Mark single-argument constructors `explicit` (next lesson).

## Key takeaways

!!! success "Key takeaways"
    - Initialize members in the member initializer list (or with default member initializers), don't assign in the body.
    - Members are initialized in declaration order, whatever order you write the list in.
    - Brace-init prefers `initializer_list` constructors: `vector<int>{3,7}` has two elements.
    - `T x();` declares a function; write `T x{};`.
    - `= default` and `= delete` control which special operations exist.

## Quiz

**Q1.** How many elements does `std::vector<int> v{5};` have? And `std::vector<int> v(5);`?

??? question "Show answer"
    `{5}`: one element with value 5 (initializer_list). `(5)`: five zero-valued elements.

**Q2.** A class declares `int a_; int b_;` and the constructor writes `: b_{1}, a_{b_}`. What's `a_`?

??? question "Show answer"
    Indeterminate (UB to read): `a_` is initialized first, from the not-yet-initialized `b_`. Initialization follows declaration order.

**Q3.** Why might you `= delete` a constructor taking `bool`?

??? question "Show answer"
    To stop accidental implicit conversions (e.g. a pointer or bool converting to int) from silently selecting another constructor.

