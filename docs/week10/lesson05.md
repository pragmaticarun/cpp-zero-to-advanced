# Lesson 10.5: Views over data: span, mdspan, string_view, and inplace_vector (preview)

<span class="stdtag">C++23</span> · about 11 minutes

## Why this matters

A function that processes audio shouldn't care whether the samples live in a `std::vector`, a
`std::array`, a C array from a driver, or memory-mapped file data. It needs "a pointer and a length". Views
give exactly that, safely typed. `std::span` does 1-D; C++23's `std::mdspan` does images, matrices and
multichannel audio; and C++26's `std::inplace_vector` gives a vector with fixed capacity and no heap —
ideal for embedded.

## `std::span<T>` recap

From Week 3: a non-owning (pointer, size) view over contiguous data. `std::span<const float>` for read-only
parameters; fixed extent `std::span<float, 4>` encodes the size in the type. `subspan`, `first`, `last` slice
without copying.

## `std::mdspan` (C++23)

A view over contiguous memory interpreted as N dimensions:

```cpp
std::mdspan img(pixels.data(), height, width);   // 2-D view
img[y, x] = 255;                                  // C++23 multidimensional subscript
```

The *layout* policy decides how indices map to memory: `layout_right` (row-major, C style, default),
`layout_left` (column-major, Fortran/BLAS style), `layout_stride`. Extents can be static or dynamic.
Support: libc++ (Clang 17+) and libstdc++ (GCC 15+); older toolchains lack it, so the example is marked
"may be unsupported" in our checker.

```cpp title="examples/week10/lesson05.cpp"
--8<-- "examples/week10/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week10/lesson05.out"
```

## Lifetime: views never own

```cpp
std::span<int> bad() { std::vector<int> v{1,2,3}; return v; }   // dangling view!
```

A view is only valid while the data it refers to is alive and not reallocated. Never return a view to a
local; be careful storing views in members.

## `std::inplace_vector<T, N>` (C++26 preview)

A vector with capacity fixed at compile time, elements stored inline — no allocation, ever. `push_back` past
capacity throws, and `try_push_back` returns null instead. It's perfect for embedded systems and for "small
lists" in hot code. No major standard library shipped it at the time of writing, so we don't compile an
example here; the Week 16 embedded lesson and the ring-buffer capstone build similar fixed-capacity
containers by hand.

```cpp
// C++26 (not compiled in this course yet)
std::inplace_vector<int, 8> v;
v.push_back(1);
if (!v.try_push_back(2)) { /* full */ }
```

## Key takeaways

!!! success "Key takeaways"
    - `std::span` is the standard 1-D view; prefer it for buffer parameters.
    - `std::mdspan` (C++23) views memory as N dimensions with pluggable layouts.
    - Views never own; returning a view to local data dangles.
    - `std::inplace_vector` (C++26) is a fixed-capacity, no-heap vector — shown as a preview.

## Quiz

**Q1.** In a row-major 3×4 `mdspan`, which memory element is `[1, 2]`?

??? question "Show answer"
    Element 1*4 + 2 = 6.

**Q2.** What's wrong with `std::span<int> f() { std::vector<int> v{1}; return v; }`?

??? question "Show answer"
    The span refers to `v`'s buffer, which is destroyed when `f` returns — a dangling view.

**Q3.** What happens when you `push_back` into a full `std::inplace_vector`?

??? question "Show answer"
    It throws `std::bad_alloc`; `try_push_back` returns a null pointer instead.

