# Week 10 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 10.1)* Why is `push_back` amortized O(1) even though reallocation is O(n)?

??? question "Show answer"
    Capacity grows geometrically, so the total copying cost over n insertions is O(n) — O(1) per insertion on average.

**Q2.** *(from 10.1)* After `v.push_back(x)` causes a reallocation, which iterators are valid?

??? question "Show answer"
    None of the old ones: all iterators, pointers and references into the vector are invalidated.

**Q3.** *(from 10.2)* Why is `vector` typically faster than `list` at 'insert in the middle' for ints?

??? question "Show answer"
    Finding the middle is O(n) for both, but vector's traversal and shift are contiguous memory operations that are cache- and prefetch-friendly, while the list chases pointers with cache misses.

**Q4.** *(from 10.2)* What does `splice` do and why is it O(1)?

??? question "Show answer"
    It relinks nodes from one list into another without copying or allocating; only pointers change.

**Q5.** *(from 10.3)* Why doesn't `counts["x"]` compile on a `const std::map`?

??? question "Show answer"
    `operator[]` may insert, so it's non-const; use `at` or `find`.

**Q6.** *(from 10.3)* What do you need for heterogeneous lookup in `std::unordered_map` (C++20)?

??? question "Show answer"
    A transparent hash (with `is_transparent`) and a transparent equality such as `std::equal_to<>`.

**Q7.** *(from 10.4)* Why does `std::stack::pop()` return `void`?

??? question "Show answer"
    Returning the removed element by value could throw (during the copy) after the element was already removed, losing it; splitting `top()` and `pop()` keeps the strong guarantee.

**Q8.** *(from 10.4)* How do you make a min-heap with `std::priority_queue`?

??? question "Show answer"
    `std::priority_queue<T, std::vector<T>, std::greater<>>`.

**Q9.** *(from 10.5)* In a row-major 3×4 `mdspan`, which memory element is `[1, 2]`?

??? question "Show answer"
    Element 1*4 + 2 = 6.

**Q10.** *(from 10.5)* What's wrong with `std::span<int> f() { std::vector<int> v{1}; return v; }`?

??? question "Show answer"
    The span refers to `v`'s buffer, which is destroyed when `f` returns — a dangling view.

**Q11.** *(from 10.6)* Why can't you call `std::sort` on a `std::list`?

??? question "Show answer"
    `std::sort` requires random-access iterators; list iterators are only bidirectional. Use `list::sort()`.

**Q12.** *(from 10.6)* What does `std::back_inserter(v)` do when assigned to?

??? question "Show answer"
    Calls `v.push_back(value)`.

