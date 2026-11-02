# Lesson 11.1: Algorithms I: searching, counting, sorting

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

You have 10,000 recorded takes and want: the first one that's clipped, how many are longer than a minute,
the top 5 by loudness, and the median duration. Each of those is a one-liner with the right algorithm —
and each of the "obvious" hand-written loops has a subtle bug or a worse complexity. Let's learn the
toolbox.

## Finding and counting

`find_if`, `count_if`, `any_of`/`all_of`/`none_of` replace most "search loops". In C++20, prefer the
`std::ranges::` versions: they take the container directly and support **projections** — a function applied
to each element before comparing:

```cpp
std::ranges::sort(takes, {}, &Take::loudness);   // sort by a member: no lambda needed
```

## Choosing a sort

| Need | Algorithm | Complexity |
|---|---|---|
| fully sorted | `sort` | O(n log n) |
| equal elements keep their order | `stable_sort` | O(n log n), may allocate |
| only the top k, sorted | `partial_sort` | O(n log k) |
| only the k-th element (e.g. median) | `nth_element` | O(n) average |

## The comparator rule

Comparators must be a **strict weak ordering**: `comp(a, a)` is false, and it's transitive. `<=` breaks the
rule — and with `std::sort` that's UB that can read out of bounds, not just "sort wrongly".

```cpp title="examples/week11/lesson01.cpp"
--8<-- "examples/week11/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week11/lesson01.out"
```

## Binary search on sorted data

`lower_bound` returns the first element not less than the value; `upper_bound` the first greater;
`equal_range` both. They're O(log n) — *if* the range is sorted by the same comparison.

## Key takeaways

!!! success "Key takeaways"
    - Name your loops: `find_if`, `count_if`, `any_of`… say what they do.
    - Projections (`&Take::seconds`) let range algorithms work on a member without lambdas.
    - Pick the cheapest sort: `partial_sort` for top-k, `nth_element` for medians, `stable_sort` to keep order.
    - Comparators must be strict weak orderings; `<=` is UB with `std::sort`.

## Quiz

**Q1.** What's the complexity of `nth_element`?

??? question "Show answer"
    O(n) on average.

**Q2.** Why is `[](int a, int b){ return a <= b; }` a broken comparator?

??? question "Show answer"
    It's not irreflexive (`comp(a, a)` is true), so it's not a strict weak ordering; `std::sort` may misbehave or read out of bounds.

**Q3.** What does `std::ranges::sort(v, {}, &T::x)` do?

??? question "Show answer"
    Sorts `v` by member `x` using the default comparator `std::ranges::less` on the projected values.

