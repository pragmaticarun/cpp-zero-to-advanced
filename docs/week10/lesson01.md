# Lesson 10.1: std::vector in depth

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

`std::vector` is a contiguous, growable array — and contiguous memory is what modern CPUs love: caches
prefetch it, SIMD chews through it. Even for operations where a linked list "should" win on paper,
`vector` often wins in practice. Let's understand it deeply: growth, invalidation, and the idioms that
keep it fast.

## Size, capacity and growth

A vector owns a heap buffer with `capacity()` slots, of which `size()` are in use. When you `push_back`
into a full vector, it allocates a bigger buffer (typically 1.5× or 2×), moves the elements over, and frees
the old one. Growth is geometric, so `push_back` is **amortized O(1)**. If you know the final size,
`reserve(n)` avoids all the reallocations.

```cpp title="examples/week10/lesson01.cpp"
--8<-- "examples/week10/lesson01.cpp"
```

**Output** (yours may differ: timing/threads):

```text
--8<-- "examples/week10/lesson01.out"
```

## Iterator invalidation: the classic bug

```cpp
for (auto it = v.begin(); it != v.end(); ++it)
    if (*it == 0) v.push_back(1);     // WRONG: push_back may reallocate -> `it` dangles (UB)
```

Rules for vector: a reallocation invalidates **all** iterators, pointers and references; `insert`/`erase`
without reallocation invalidate those **at or after** the point. Holding `&v[0]` across a `push_back` is the
same bug. Prefer indices when you must modify while iterating, or collect changes and apply them after.

## Erasing elements

C++20's `std::erase_if(v, pred)` does it in one line. Before C++20 you'd use the *erase-remove idiom*:
`v.erase(std::remove_if(v.begin(), v.end(), pred), v.end());` — `remove_if` only shuffles the kept elements
forward; `erase` chops off the tail.

## `emplace_back` vs `push_back`

`emplace_back(args...)` constructs the element in place from constructor arguments; `push_back(obj)` copies or
moves an existing object. For an already-built object they're the same. Note `emplace_back` can call
`explicit` constructors, which can hide mistakes — prefer `push_back` unless you're constructing in place.

!!! warning "`std::vector<bool>` is not a container of bools"
    It packs bits, so `v[i]` returns a proxy object, not `bool&`; `auto& b = v[0];` doesn't compile and
    `&v[0]` isn't a `bool*`. Use `std::vector<char>`, `std::bitset` or `std::vector<std::uint8_t>` when you
    need real elements.

## Key takeaways

!!! success "Key takeaways"
    - `vector` is contiguous and cache-friendly; growth is geometric so `push_back` is amortized O(1).
    - `reserve` when you know the size; reallocation invalidates all iterators, pointers and references.
    - Use `std::erase_if` (C++20) or erase-remove to delete elements.
    - `std::vector<bool>` is a bit-packed special case with proxy references.

## Quiz

**Q1.** Why is `push_back` amortized O(1) even though reallocation is O(n)?

??? question "Show answer"
    Capacity grows geometrically, so the total copying cost over n insertions is O(n) — O(1) per insertion on average.

**Q2.** After `v.push_back(x)` causes a reallocation, which iterators are valid?

??? question "Show answer"
    None of the old ones: all iterators, pointers and references into the vector are invalidated.

**Q3.** What does `std::remove` actually do?

??? question "Show answer"
    It moves the kept elements to the front and returns the new logical end; it doesn't change the size — you must `erase` the tail.

