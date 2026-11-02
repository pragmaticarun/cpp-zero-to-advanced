# Lesson 16.3: Design patterns in modern C++

<span class="stdtag">C++20</span> · about 13 minutes

## Why this matters

Classic design patterns were described for 1990s Java and C++. Modern C++ often expresses them more simply:
a strategy can be a lambda, a visitor can be `std::visit` over a variant, and an observer must care about
*lifetimes* (who unsubscribes when an object dies?). Knowing the modern form keeps designs small.

## Modern forms of classic patterns

| Pattern | Classic | Modern C++ |
|---|---|---|
| Strategy | interface + subclasses | `std::function`, template parameter, or concept |
| Visitor | double dispatch with `accept` | `std::variant` + `std::visit` (closed set of types) |
| Observer | raw listener pointers | subscription tokens / `weak_ptr` to avoid dangling |
| Factory | `switch` on type name | registry map of creator functions |
| Template method | virtual hooks | NVI (Week 6) or CRTP (Week 8) |
| Scope guard | try/finally | RAII object with a lambda |

```cpp title="examples/week16/lesson03.cpp"
--8<-- "examples/week16/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week16/lesson03.out"
```

The observer uses `weak_ptr` so a destroyed listener is skipped automatically — no dangling callbacks.

## When *not* to use a pattern

Patterns are vocabulary, not goals. If a plain function solves it, write a plain function. Every
indirection (virtual call, `std::function`, registry) costs readability; add it when you need the
flexibility, not before.

## Key takeaways

!!! success "Key takeaways"
    - Many patterns shrink in modern C++: strategy = callable, visitor = `std::visit`.
    - Observers must handle listener lifetime; `weak_ptr` or tokens avoid dangling callbacks.
    - Registries of creator functions make extensible factories.
    - Use a pattern when you need its flexibility, not by default.

## Quiz

**Q1.** When is `std::variant` + `std::visit` better than a virtual-function hierarchy?

??? question "Show answer"
    When the set of types is closed and known, and you want to add operations easily without touching the types.

**Q2.** What bug does `weak_ptr` prevent in the observer?

??? question "Show answer"
    Calling a listener that has been destroyed (dangling callback).

**Q3.** What's the cost of using `std::function` for a strategy?

??? question "Show answer"
    Type erasure: possible heap allocation and an indirect call that's hard to inline; a template parameter avoids it.

