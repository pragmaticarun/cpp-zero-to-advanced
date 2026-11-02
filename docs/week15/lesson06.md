# Lesson 15.6: Security hardening and the C++ Core Guidelines

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

Roughly 70% of serious security bugs in large C and C++ codebases are memory-safety bugs. Governments and
companies now ask hard questions about C++. The honest answer: modern C++ with good habits and hardened
builds eliminates most of these bugs — but only if you actually use them. This lesson collects the habits.

## Habits that eliminate whole bug classes

| Bug class | Modern C++ habit |
|---|---|
| Buffer overflow | containers + `std::span`, range-for, hardened library checks |
| Use-after-free / leaks | RAII, smart pointers, no raw owning pointers |
| Dangling references | don't return references to locals; watch `string_view`/`span` lifetimes |
| Integer overflow / sign bugs | `std::cmp_less`, `std::in_range`, checked narrowing |
| Uninitialized memory | always initialize; `-ftrivial-auto-var-init=zero`; C++26 makes it *erroneous behaviour* |
| Type confusion | no C casts; `std::variant` over unions; `dynamic_cast` when downcasting |

## Hardened builds

- `-D_GLIBCXX_ASSERTIONS` (libstdc++) or `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST` (libc++)
  turns `operator[]` out-of-bounds and similar precondition violations into a trap. Cost is usually low
  single-digit percent; many vendors ship with it enabled.
- `-D_FORTIFY_SOURCE=3 -O2`, `-fstack-protector-strong`, `-fstack-clash-protection`, `-fPIE -pie`,
  `-Wl,-z,relro,-z,now` — see the OpenSSF compiler hardening guide.

```cpp title="examples/week15/lesson06.cpp"
--8<-- "examples/week15/lesson06.cpp"
```

**Output**:

```text
--8<-- "examples/week15/lesson06.out"
```

## The C++ Core Guidelines

The [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/) (Stroustrup & Sutter) are the
community's style and safety rulebook: R.* for resources, F.* for functions, ES.* for expressions, CP.* for
concurrency. The GSL library provides helpers like `gsl::not_null<T*>` and `gsl::narrow<T>` (throws on
lossy conversion). clang-tidy can enforce many rules automatically.

## Key takeaways

!!! success "Key takeaways"
    - Most memory-safety bugs are prevented by RAII, containers, spans and no raw owning pointers.
    - Ship hardened builds: library assertions, FORTIFY_SOURCE, stack protector, PIE/RELRO.
    - Use `std::cmp_less`/`std::in_range` and checked narrowing for integer safety.
    - Follow the C++ Core Guidelines and enforce them with clang-tidy.

## Quiz

**Q1.** What does `-D_GLIBCXX_ASSERTIONS` do?

??? question "Show answer"
    Enables libstdc++ precondition checks, e.g. trapping on out-of-bounds `vector::operator[]`.

**Q2.** Why is `-1 < 3u` false?

??? question "Show answer"
    -1 converts to a huge unsigned value; use `std::cmp_less(-1, 3u)` which compares mathematically.

**Q3.** Name three Core Guidelines-backed habits that prevent use-after-free.

??? question "Show answer"
    RAII ownership, smart pointers instead of raw owning pointers, not storing references/views that outlive their owner.

