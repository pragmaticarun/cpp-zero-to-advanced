# Lesson 10.2: array, deque, list, and forward_list

<span class="stdtag">C++20</span> · about 10 minutes

## Why this matters

`std::vector` is the default, but not the only answer. A fixed-size table of filter coefficients doesn't
need the heap at all (`std::array`). A queue that grows at both ends wants `std::deque`. And sometimes you
genuinely need stable element addresses or O(1) splicing (`std::list`). Let's see when each one earns its
place — and measure why lists usually don't.

| Container | Layout | Fast operations | Iterators stable? |
|---|---|---|---|
| `array<T,N>` | inline, fixed | everything; no heap | yes (never reallocates) |
| `vector<T>` | contiguous heap block | back insert/erase, random access | until reallocation |
| `deque<T>` | blocks of elements | front *and* back insert, random access | references stable for end inserts; iterators not |
| `list<T>` | doubly linked nodes | insert/erase anywhere given an iterator, `splice` | yes |
| `forward_list<T>` | singly linked nodes | same, less memory, forward only | yes |

## Big-O isn't everything

Inserting in the middle of a `list` is O(1) — *once you have the iterator*. Finding the position is O(n)
pointer chasing, with a likely cache miss per node. A `vector` insert is O(n) but it's a `memmove` of
contiguous memory, which modern CPUs do extremely fast. The example times both (timings are printed for
you to look at on your machine; they vary).

```cpp title="examples/week10/lesson02.cpp"
--8<-- "examples/week10/lesson02.cpp"
```

**Output** (yours may differ: timing/threads):

```text
--8<-- "examples/week10/lesson02.out"
```

## When `list` really wins

- You need iterators/pointers to elements to stay valid while others are inserted/erased (e.g. an LRU
  cache: `list` + `unordered_map` of iterators).
- You move ranges between lists with `splice` in O(1) without copying elements.
- Elements are huge and non-movable.

`std::to_array` (C++20) creates a `std::array` with the size deduced: `auto a = std::to_array({1, 2, 3});`.

## Key takeaways

!!! success "Key takeaways"
    - `std::array` for fixed sizes (no heap); `deque` for both-end queues; `vector` for almost everything else.
    - Linked lists have O(1) insertion given an iterator but terrible cache behaviour; finding the position dominates.
    - Choose `list` for stable iterators and O(1) `splice`, not for 'fast insertion'.
    - Measure on your hardware — complexity classes hide constant factors.

## Quiz

**Q1.** Why is `vector` typically faster than `list` at 'insert in the middle' for ints?

??? question "Show answer"
    Finding the middle is O(n) for both, but vector's traversal and shift are contiguous memory operations that are cache- and prefetch-friendly, while the list chases pointers with cache misses.

**Q2.** What does `splice` do and why is it O(1)?

??? question "Show answer"
    It relinks nodes from one list into another without copying or allocating; only pointers change.

**Q3.** Does `std::array` allocate on the heap?

??? question "Show answer"
    No — its elements are stored inline in the object (on the stack for a local).

