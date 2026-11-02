# Lesson 6.1: Inheritance basics: base classes, access, construction order

<span class="stdtag">C++20</span> · about 10 minutes

## Why this matters

Suppose every audio effect in your app — gain, echo, low-pass filter — has a name, an enabled flag and a
bypass switch. Writing those three things in every class is tedious and error-prone. Inheritance lets a
derived class *be a kind of* base class and get its members. Let's see the mechanics first; next lesson
we'll add the real superpower, virtual functions.

## Is-a relationships

```cpp
class Effect { ... };                 // base class
class Gain : public Effect { ... };   // Gain *is an* Effect
```

With **public** inheritance, a `Gain` can be used wherever an `Effect&` or `Effect*` is expected. That's
the only kind of inheritance you'll use regularly. (`private` inheritance means "implemented in terms of"
and is rare; prefer a member.)

| Base member is... | accessible in derived? | accessible to users of derived (public inheritance)? |
|---|---|---|
| `public` | yes | yes |
| `protected` | yes | no |
| `private` | no | no |

## Construction order

A derived object contains a base *subobject*. Construction goes **base first, then members (in
declaration order), then the derived constructor body**. Destruction runs in exactly the reverse order.
You call a base constructor from the member initializer list. If the derived class adds no state of its own,
`using Base::Base;` (C++11) inherits the base constructors.

```cpp title="examples/week06/lesson01.cpp"
--8<-- "examples/week06/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week06/lesson01.out"
```

## The wrong way: name hiding

```cpp
struct Base    { void process(int); void process(double); };
struct Derived : Base { void process(int); };   // hides BOTH Base::process overloads
Derived d; d.process(2.5);                     // calls Derived::process(int) with 2 — surprise!
```

Declaring any `process` in `Derived` hides all of the base's `process` overloads. Bring them back with
`using Base::process;` in `Derived`.

!!! tip "Pro tip: prefer composition"
    "Has-a" is usually a member; "is-a" is inheritance. If you inherit only to reuse code, a member object
    is almost always simpler and more flexible.

## Key takeaways

!!! success "Key takeaways"
    - Public inheritance models *is-a*; a derived object contains a base subobject.
    - Construction: bases, then members in declaration order, then the body; destruction is the reverse.
    - A member function in a derived class hides all base overloads with that name; `using Base::f;` restores them.
    - Prefer composition for code reuse.

## Quiz

**Q1.** In what order are these constructed: base `B`, members `m1`, `m2` of derived `D`, and `D`'s constructor body?

??? question "Show answer"
    `B`, then `m1`, then `m2` (declaration order), then the body of `D`'s constructor.

**Q2.** What does `using Base::Base;` do?

??? question "Show answer"
    Inherits Base's constructors into the derived class (C++11).

**Q3.** Why might `d.process(2.5)` call `Derived::process(int)`?

??? question "Show answer"
    Because `Derived` declares `process`, which hides all `Base::process` overloads; the only candidate takes `int` and 2.5 converts to it.

