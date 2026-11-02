# Lesson 4.1: Classes, encapsulation, and const member functions

<span class="stdtag">C++20</span> · about 10 minutes

## Why this matters

Imagine a `Volume` type whose value must always be between 0 and 100. If it's a plain struct with a public
`int`, any line of code anywhere can set it to -7, and you'll find out three weeks later in a bug report.
A class lets you make the data private and only allow changes through functions that keep the rule —
the *invariant* — true. That's encapsulation, and it's what makes large programs manageable.

## `class` and `struct` are almost the same

The only difference: members of a `struct` are public by default; members of a `class` are private by
default. Convention: use `struct` for plain bundles of data with no invariants, and `class` when there's an
invariant to protect.

## Protecting an invariant

```cpp title="examples/week04/lesson01.cpp"
--8<-- "examples/week04/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week04/lesson01.out"
```

Let's walk through the design:

- `level_` is **private**: only member functions can touch it.
- The constructor and `set()` both go through `clamp`, so the invariant "0 ≤ level ≤ 100" holds for every
  `Volume` that ever exists.
- `get()` is marked **`const`**: it promises not to modify the object. That's what allows it to be called
  on a `const Volume&`. Forgetting `const` on getters is a very common mistake — the moment someone has a
  `const` reference, your class becomes unusable.
- `this` is a pointer to the current object. You rarely need to write it explicitly.

## `mutable`: the escape hatch

Sometimes a `const` function legitimately needs to change something that isn't part of the observable state
— a cache, or a mutex. Mark that member `mutable`. Use it sparingly: it's for implementation details only.

## The wrong way: getters and setters for everything

```cpp
class Volume {
    int level_;
public:
    int  getLevel() const { return level_; }
    void setLevel(int l)  { level_ = l; }     // no checking: this is a struct with extra steps
};
```

A setter that doesn't enforce anything adds ceremony without protection. Either there's an invariant (then
enforce it) or there isn't (then use a plain struct).

## Ref-qualifiers (advanced, optional)

You can overload a member function on whether `*this` is an lvalue or an rvalue: `get() &` vs `get() &&`.
This lets a temporary give away its internals cheaply. You'll appreciate it after Week 5; C++23's
*deducing this* (Week 8) makes it much easier to write.

## Key takeaways

!!! success "Key takeaways"
    - `class` and `struct` differ only in default access; use `class` when you have an invariant.
    - Make data private and enforce invariants in constructors and member functions.
    - Mark every member function that doesn't modify the object `const`.
    - `mutable` is for caches/mutexes — not for avoiding thinking about const.

## Quiz

**Q1.** Why can't you call a non-const member function through a `const Volume&`?

??? question "Show answer"
    A const reference only allows operations that promise not to modify the object, i.e. `const` member functions.

**Q2.** What's the type of `this` inside a `const` member function of `Volume`?

??? question "Show answer"
    `const Volume*`.

**Q3.** When is a plain `struct` with public members the right choice?

??? question "Show answer"
    When the members are independent and any combination of values is valid — there's no invariant to protect.

