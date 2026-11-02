# Lesson 12.1: unique_ptr and custom deleters

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

Back in Week 3 we saw how raw `new`/`delete` leaks and double-frees. `std::unique_ptr` fixes that with
*zero* overhead: it's exactly one pointer, and its destructor calls `delete`. With a custom deleter it
manages *any* resource — `FILE*`, a codec handle from a C library, an OpenGL texture. It should be your
default for owning heap objects.

## Unique ownership

```cpp
auto codec = std::make_unique<Codec>(48000);   // owns the Codec
auto other = std::move(codec);                 // ownership transferred; codec is now null
```

`unique_ptr` is move-only, so "who owns this" is visible in the code: you can't accidentally share it.

## Custom deleters for C resources

```cpp
struct FileCloser { void operator()(std::FILE* f) const noexcept { std::fclose(f); } };
using File = std::unique_ptr<std::FILE, FileCloser>;
```

A stateless function-object deleter keeps `sizeof(File) == sizeof(FILE*)`. A function-pointer deleter
adds a pointer's worth of size. C++23's `std::out_ptr` adapts a `unique_ptr` to C APIs that return a
resource through a `T**` out-parameter.

```cpp title="examples/week12/lesson01.cpp"
--8<-- "examples/week12/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week12/lesson01.out"
```

## Passing smart pointers (C++ Core Guidelines R.30–R.37)

| You want to... | Parameter type |
|---|---|
| just use the object | `T&` or `T*` (nullable) — **not** a smart pointer |
| take ownership | `std::unique_ptr<T>` by value |
| maybe reseat the caller's pointer | `std::unique_ptr<T>&` |
| share ownership | `std::shared_ptr<T>` by value |

## Pitfalls

- Two `unique_ptr`s from the same raw pointer → double free.
- `unique_ptr<T>` for an array allocated with `new[]` → use `unique_ptr<T[]>` (or better, `std::vector`).
- `release()` gives up ownership *without* deleting — the caller must now free it.

## Key takeaways

!!! success "Key takeaways"
    - `unique_ptr` is zero-overhead exclusive ownership; transfer it with `std::move`.
    - Custom deleters manage any resource; stateless deleters add no size.
    - Pass `T&`/`T*` to functions that only use an object; pass `unique_ptr` by value to transfer ownership.
    - `std::out_ptr` (C++23) bridges smart pointers and C out-parameter APIs.

## Quiz

**Q1.** What's `sizeof(std::unique_ptr<int>)` on a typical 64-bit platform?

??? question "Show answer"
    8 bytes — the same as a raw pointer (with the default deleter).

**Q2.** How should a function that only reads a `Codec` take it?

??? question "Show answer"
    By `const Codec&` (or `const Codec*` if null is allowed), not by smart pointer.

**Q3.** What does `release()` do?

??? question "Show answer"
    Returns the raw pointer and sets the unique_ptr to null without deleting; the caller becomes responsible for freeing it.

