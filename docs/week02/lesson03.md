# Lesson 2.3: References, const, and how to pass parameters

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

Suppose a function processes a 10 MB video frame stored in a `std::vector<std::uint8_t>`. If you
write `void process(std::vector<std::uint8_t> frame)`, every call copies 10 MB. Change one character —
`const std::vector<std::uint8_t>& frame` — and the copy disappears. References are how C++ lets you
refer to an existing object without copying it. Let's build the intuition.

## A reference is another name for an existing object

```cpp
int volume = 5;
int& v = volume;   // v *is* volume, under another name
v = 7;             // volume is now 7
```

A reference must be initialized, and it can never be "re-seated" to refer to something else. Assigning
to it assigns to the object it refers to.

## Three ways to pass a parameter

| You want to... | Write | Why |
|---|---|---|
| read a cheap value (`int`, `double`, small struct) | `void f(int x)` | copying a few bytes is the fastest thing there is |
| read an expensive object | `void f(const std::string& s)` | no copy, can't modify |
| modify the caller's object | `void f(std::string& s)` | caller sees the change |

(There's a fourth — `T&&` — for "I want to steal from a temporary". That's Week 5's move semantics.)

```cpp title="examples/week02/lesson03.cpp"
--8<-- "examples/week02/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week02/lesson03.out"
```

## `const T&` binds to temporaries

`print_twice(std::string{"temp"})` works even though the argument is a temporary: a `const` reference may
bind to a temporary, and the temporary lives until the end of the full expression. A *non-const*
reference can't bind to a temporary — that would let you modify a value that's about to disappear.

## `auto` and references

`auto` deduces a *value* type: it strips references and top-level `const`.

```cpp
const std::string& name = get_name();
auto a = name;          // std::string — a copy!
const auto& b = name;   // const std::string& — no copy
```

So when you want a reference, ask for one: `auto&` or `const auto&`.

## The big danger: dangling references

A reference doesn't keep its object alive. Returning a reference to a local is the classic mistake:

```cpp
const std::string& make_label() {
    std::string s = "label";
    return s;          // WRONG: s is destroyed when the function returns
}                      // the caller gets a dangling reference -> UB
```

Compilers warn about this simple case (`-Wreturn-local-addr` / `-Wreturn-stack-address`), but subtler
versions — references into a vector that later reallocates, for example — need you to think about
**lifetime**. That's next lesson.

!!! tip "Pro tip"
    Return by value. Thanks to copy elision and move semantics (Week 5), returning a `std::string` or
    `std::vector` by value is cheap. Return references only to things that clearly outlive the call
    (like a member of `*this`).

## Key takeaways

!!! success "Key takeaways"
    - A reference is an alias for an existing object; it must be initialized and can't be re-seated.
    - Pass cheap types by value, expensive ones by `const&`, and use `&` only to modify the caller's object.
    - `auto` deduces a value type; write `const auto&` when you want a reference.
    - References don't extend lifetimes (except a const& bound directly to a temporary) — beware dangling.

## Quiz

**Q1.** Why can't `void f(std::string& s)` be called as `f(std::string{"x"})`?

??? question "Show answer"
    A non-const lvalue reference can't bind to a temporary (an rvalue). Use `const std::string&` (or `std::string&&` / by value if you want to consume it).

**Q2.** Given `const std::vector<int>& r = v;`, what is the type of `auto x = r;`?

??? question "Show answer"
    `std::vector<int>` — a full copy, because `auto` drops the reference and top-level const.

**Q3.** Is it fine to pass an `int` by `const int&`?

??? question "Show answer"
    It works, but by value is simpler and usually faster: an `int` fits in a register; a reference may force it into memory and introduces aliasing questions.

