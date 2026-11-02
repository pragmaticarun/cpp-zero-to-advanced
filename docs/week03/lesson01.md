# Lesson 3.1: Arrays: C arrays, std::array, and a first look at std::span

<span class="stdtag">C++20</span> · about 10 minutes

## Why this matters

Audio and video code is full of fixed-size buffers: a 1024-sample FFT window, a 16-entry lookup table,
a 4×4 matrix. Arrays are the simplest container there is — but C-style arrays have a nasty habit of
forgetting their own size the moment you pass them to a function. Let's see the problem and the modern fixes.

## C arrays, and how they forget their size

```cpp
int window[4] = {1, 2, 3, 4};
std::cout << sizeof(window);     // 16: the whole array (4 * sizeof(int))

void f(int a[4]) {               // looks like an array parameter...
    std::cout << sizeof(a);      // 8: it's really `int* a`!
}
```

When you pass a C array to a function, it **decays** to a pointer to its first element. The size is gone
— the `[4]` in the parameter is ignored. This is where countless buffer overflows begin.

## `std::array`: an array that behaves like a value

`std::array<int, 4>` is a thin wrapper around a C array with zero overhead. It knows its size, can be
copied and compared, and can be returned from functions.

## `std::span`: "a view of some contiguous elements" (C++20)

When a function just needs to *look at* a sequence of elements, take a `std::span<const T>`. A span is a
pointer plus a length; it doesn't own anything. It accepts C arrays, `std::array`, and `std::vector`
alike — and it can't forget its size.

```cpp title="examples/week03/lesson01.cpp"
--8<-- "examples/week03/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week03/lesson01.out"
```

## Bounds

`a[i]` with `i` out of range is **undefined behaviour** — no exception, no guaranteed crash. `std::array`
and `std::vector` offer `.at(i)` which throws `std::out_of_range`. In debug builds you can also turn on
library assertions (`-D_GLIBCXX_ASSERTIONS` for libstdc++, hardening modes in libc++) to catch bad
`operator[]` indexes; many distributions enable that by default now.

!!! tip "Pro tip"
    Rule of thumb: **own** data with `std::array` / `std::vector`; **pass** it to functions as
    `std::span<const T>` (read) or `std::span<T>` (write). We'll revisit spans and `mdspan` in Week 10.

## Key takeaways

!!! success "Key takeaways"
    - C arrays decay to pointers when passed to functions and lose their size.
    - `std::array<T, N>` is a zero-overhead fixed array with value semantics.
    - Pass contiguous data as `std::span<const T>` / `std::span<T>` — one signature for all containers.
    - Out-of-bounds `[]` is UB; `.at()` throws; library hardening catches it in debug builds.

## Quiz

**Q1.** Inside `void f(int a[10])`, what is `sizeof(a)` on a 64-bit system?

??? question "Show answer"
    8 — the parameter is actually `int*`; the 10 is ignored.

**Q2.** Does `std::span` own its elements?

??? question "Show answer"
    No. It is a non-owning view (pointer + size). The underlying storage must outlive the span.

**Q3.** What's the difference between `arr[10]` and `arr.at(10)` for a `std::array<int, 4>`?

??? question "Show answer"
    `arr[10]` is undefined behaviour; `arr.at(10)` throws `std::out_of_range`.

