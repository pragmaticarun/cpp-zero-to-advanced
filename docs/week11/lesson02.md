# Lesson 11.2: Algorithms II: transforming, removing, and numeric

<span class="stdtag">C++23</span> · about 11 minutes

## Why this matters

Normalize a buffer, keep only the takes above a threshold, compute RMS loudness, build a running total —
these are transforms, filters and reductions. The standard library has them all, including parallel-ready
versions (`reduce`, `transform_reduce`) that we'll run on multiple cores in Week 14.

## Transform, filter, replace

```cpp
std::ranges::transform(in, out.begin(), [](float x) { return x * gain; });
std::ranges::copy_if(takes, std::back_inserter(good), is_good);
```

Output algorithms *write through an iterator*; they never grow the destination. Writing into an empty
vector's `begin()` is UB — use `std::back_inserter` or size the destination first.

## Removing duplicates

`unique` removes *consecutive* duplicates (so sort first) and, like `remove`, returns the new end — then
`erase`.

## Numeric reductions

- `accumulate(first, last, init)` — left fold, strictly in order. **The init type decides the result type**:
  `accumulate(v.begin(), v.end(), 0)` on doubles sums into an `int`!
- `reduce` — like accumulate but may reorder (associative + commutative ops), enabling parallelism.
- `transform_reduce` — map then reduce: dot products, RMS.
- `partial_sum` / `inclusive_scan` / `exclusive_scan` — running totals.
- C++23 `std::ranges::fold_left` — the ranges-style accumulate.

```cpp title="examples/week11/lesson02.cpp"
--8<-- "examples/week11/lesson02.cpp"
```

**Output**:

```text
--8<-- "examples/week11/lesson02.out"
```

## Set and heap algorithms

On *sorted* ranges, `set_intersection`, `set_union`, `set_difference` and `includes` run in linear time.
Heap algorithms let you keep a heap inside your own vector — what `priority_queue` uses internally.

!!! tip "Pro tip: `std::midpoint`"
    `(a + b) / 2` can overflow; `std::midpoint(a, b)` (C++20) can't. It also handles pointers and floats
    correctly.

## Key takeaways

!!! success "Key takeaways"
    - Output algorithms write through iterators; use `back_inserter` or pre-size the destination.
    - `unique` and `remove` return a new end; erase the tail.
    - `accumulate`'s init value sets the result type — `0` vs `0.0` matters.
    - `reduce`/`transform_reduce` allow reordering (and parallelism); scans give running totals.

## Quiz

**Q1.** What's wrong with `std::accumulate(v.begin(), v.end(), 0)` for `std::vector<double>`?

??? question "Show answer"
    The accumulator is `int`, so each partial sum is converted to int — the result is truncated.

**Q2.** Why must you sort before `std::unique` to remove all duplicates?

??? question "Show answer"
    `unique` only collapses consecutive equal elements.

**Q3.** How does `reduce` differ from `accumulate`?

??? question "Show answer"
    `reduce` may apply the operation in any order/grouping (requiring associativity and commutativity for deterministic results), which enables parallel execution; `accumulate` is strictly left-to-right.

