# Lesson 10.6: Iterators and iterator categories

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

Iterators are the glue of the standard library: algorithms don't know about containers, only about
iterators. If you make *your* data structure provide iterators, every algorithm — `sort`, `find`,
`accumulate`, range-for, ranges — works on it for free. This lesson shows the categories and builds an
iterator for a ring buffer, the core of our embedded capstone.

## Categories

Each category adds capabilities; algorithms require the weakest category they need:

| Category | Adds | Example |
|---|---|---|
| input | read once, `++` | `istream_iterator` |
| forward | multi-pass | `forward_list` |
| bidirectional | `--` | `list`, `map` |
| random access | `+ n`, `[]`, `<` | `deque` |
| contiguous (C++20) | elements adjacent in memory | `vector`, `array`, `span` |

`std::sort` needs random access, which is why `std::list` has its own `sort()` member.

## Adaptors

- `std::back_inserter(v)` — an output iterator that calls `push_back`.
- `std::make_reverse_iterator`, `rbegin/rend`.
- `std::make_move_iterator` — moves instead of copies when used with algorithms.
- `std::istream_iterator<T>` — reads values from a stream.

## Writing your own

A C++20 iterator needs: `value_type`, `difference_type`, `operator*`, `operator++` (pre and post), and
`operator==`. Satisfying `std::forward_iterator` then gets you every forward algorithm. Use `static_assert`
with the concept to check.

```cpp title="examples/week10/lesson06.cpp"
--8<-- "examples/week10/lesson06.cpp"
```

**Output**:

```text
--8<-- "examples/week10/lesson06.out"
```

## Sentinels

In C++20 ranges, the end of a range can be a *different type* than the iterator — a sentinel. E.g. "until
the null terminator" doesn't need a precomputed end pointer. We'll use this in Week 11.

## Key takeaways

!!! success "Key takeaways"
    - Algorithms work on iterators; the category determines which algorithms apply.
    - Iterator adaptors (`back_inserter`, reverse, move, stream) connect containers, streams and algorithms.
    - A custom iterator with a few members unlocks the whole algorithm library; check with C++20 concepts.
    - Sentinels let a range's end be a different type than its iterator.

## Quiz

**Q1.** Why can't you call `std::sort` on a `std::list`?

??? question "Show answer"
    `std::sort` requires random-access iterators; list iterators are only bidirectional. Use `list::sort()`.

**Q2.** What does `std::back_inserter(v)` do when assigned to?

??? question "Show answer"
    Calls `v.push_back(value)`.

**Q3.** What minimum members does a C++20 forward iterator need?

??? question "Show answer"
    `value_type`, `difference_type`, `operator*`, pre- and post-increment, equality comparison, and default constructibility.

