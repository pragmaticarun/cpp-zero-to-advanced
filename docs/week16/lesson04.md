# Lesson 16.4: API and library design

<span class="stdtag">C++23</span> · about 12 minutes

## Why this matters

`set_volume(0.8, 1)` — is that 80% on channel 1, or volume 1 with 0.8 seconds fade? Good APIs make
correct use easy and incorrect use hard *at compile time*. A library's interface outlives its
implementation by years; this lesson is about getting it right.

## Principles

1. **Make illegal states unrepresentable**: strong types (`Gain`, `Channel`, `Milliseconds`) instead of
   naked `double`/`int`; enums instead of `bool` flags.
2. **Mark results that must be used**: `[[nodiscard("check the error")]]`.
3. **Pick one error policy** per library (Week 9) and document it.
4. **Value semantics and const-correctness**: take `const T&`/`std::string_view`/`std::span` for inputs,
   return values, avoid out-parameters.
5. **Evolve without breaking**: `[[deprecated("use X")]]`, inline namespaces for versioning, keep ABI
   policies explicit (pimpl, Week 15).

```cpp title="examples/week16/lesson04.cpp"
--8<-- "examples/week16/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week16/lesson04.out"
```

## Checklist for a public header

- Includes only what it needs (consider forward declarations).
- No `using namespace` at header scope.
- Everything in a project namespace.
- Every function documents preconditions, errors, and ownership.
- Tests use only the public API.

## Key takeaways

!!! success "Key takeaways"
    - Strong types and enums turn argument mix-ups into compile errors.
    - `[[nodiscard]]` and `std::expected` make errors hard to ignore.
    - Use `[[deprecated]]` and inline namespaces to evolve APIs without breaking users.
    - Keep public headers minimal, namespaced and fully documented.

## Quiz

**Q1.** Why is `void f(bool fast, bool safe)` a weak signature?

??? question "Show answer"
    Call sites like `f(true, false)` are unreadable and easy to swap; use enums or strong types.

**Q2.** What does an inline namespace give you for versioning?

??? question "Show answer"
    Its contents are accessible from the enclosing namespace by default, while older versions remain addressable explicitly (and mangled names differ per version).

**Q3.** What happens when a caller ignores a `[[nodiscard]]` result?

??? question "Show answer"
    The compiler warns (an error with `-Werror`).

