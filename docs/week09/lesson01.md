# Lesson 9.1: Exceptions: throw, try, catch, and stack unwinding

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

You're parsing a playlist file. Fifteen functions deep, you discover the file is corrupt. With error codes,
every one of those fifteen functions must check and pass the error up. Exceptions jump straight to the
code that can handle it — and RAII ensures everything in between is cleaned up on the way. That's the
idea; the details (what to throw, what to catch, what it costs) are this lesson.

## The basics

```cpp
if (!file) throw std::runtime_error{"cannot open " + path};
...
try { load(path); }
catch (const std::runtime_error& e) { std::cerr << e.what(); }
```

- **Throw by value, catch by `const&`.** Catching by value slices and copies.
- Handlers are tried in order; put derived types before base types.
- `catch (...)` catches anything; `throw;` rethrows the current exception unchanged.

## Stack unwinding

When an exception propagates, every fully constructed local object on the way is destroyed — that's why
RAII (Week 4) makes exception-safe code natural. The example prints destructors as the stack unwinds.
If no handler is found, `std::terminate` is called (and whether the stack is unwound first is
implementation-defined).

```cpp title="examples/week09/lesson01.cpp"
--8<-- "examples/week09/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week09/lesson01.out"
```

## The standard hierarchy

`std::exception` ← `std::logic_error` (bugs: `invalid_argument`, `out_of_range`, `length_error`) and
`std::runtime_error` (environment: `range_error`, `overflow_error`, `system_error`), plus `bad_alloc`,
`bad_cast`, `bad_variant_access`, `bad_optional_access`... Derive your own from `std::runtime_error` and
add context.

## Nesting and transporting

`std::throw_with_nested` wraps the current exception inside a new one with more context ("while loading
playlist X: cannot open file Y"). `std::exception_ptr` lets you carry an exception to another thread —
`std::future` uses it.

## Costs and no-exception builds

Mainstream implementations use "zero-cost" tables: **no** cost on the happy path, but a throw is slow
(microseconds) and binaries grow. So: exceptions for *exceptional* failures, not for control flow. Some
domains (games, embedded, parts of Android/Google code) compile with `-fno-exceptions`; then `throw` doesn't
compile and allocation failure terminates. Lesson 4 shows the alternatives.

## Key takeaways

!!! success "Key takeaways"
    - Throw by value, catch by `const&`, most-derived handlers first.
    - Stack unwinding destroys locals, so RAII makes cleanup automatic.
    - Use `throw_with_nested` for context and `exception_ptr` to transport exceptions.
    - Exceptions are free when not thrown but slow when thrown; reserve them for genuinely exceptional failures.

## Quiz

**Q1.** Why catch by `const&` rather than by value?

??? question "Show answer"
    Catching by value copies and slices derived exceptions to the caught type; a reference preserves the dynamic type and avoids the copy.

**Q2.** What happens if an exception is never caught?

??? question "Show answer"
    `std::terminate` is called.

**Q3.** What's the difference between `throw;` and `throw e;` in a handler?

??? question "Show answer"
    `throw;` rethrows the original exception object unchanged; `throw e;` throws a copy of `e`'s static type, possibly slicing.

