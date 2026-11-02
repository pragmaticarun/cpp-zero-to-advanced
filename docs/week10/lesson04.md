# Lesson 10.4: Container adaptors, flat_map and flat_set

<span class="stdtag">C++23</span> · about 10 minutes

## Why this matters

A task scheduler needs "give me the highest-priority job". An undo system needs "last in, first out". These
aren't new data structures — they're *interfaces* on top of existing containers, called adaptors. And
C++23 adds `flat_map`, a map that stores its data in sorted vectors, because for many workloads that beats a
tree by a wide margin.

## Adaptors

| Adaptor | Default underlying container | Operations |
|---|---|---|
| `stack<T>` | `deque<T>` | `push`, `pop`, `top` |
| `queue<T>` | `deque<T>` | `push`, `pop`, `front`, `back` |
| `priority_queue<T>` | `vector<T>` (binary heap) | `push`, `pop`, `top` = largest |

`pop()` returns `void` — read `top()` first. (That's for exception safety: returning the popped element
by value could throw after it's been removed.) For a min-heap pass `std::greater<>` as comparator.

```cpp title="examples/week10/lesson04.cpp"
--8<-- "examples/week10/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week10/lesson04.out"
```

## `flat_map` and `flat_set` (C++23)

They keep keys (and values) in sorted contiguous containers and binary-search them. Compared with `std::map`:

- Lookups and iteration: faster (cache-friendly, no pointer chasing).
- Insertions/erasures in the middle: O(n) (elements shift).
- Iterators invalidated by insertions (unlike `map`).

Great for data that's built once and read many times — configs, lookup tables, small maps. Compiler status:
libc++ ships them; GCC's libstdc++ added `<flat_map>` in GCC 15. The second example is therefore marked
"may be unsupported" in our checker. Before C++23, a sorted `std::vector` + `std::lower_bound` gives you the
same thing by hand.

```cpp title="examples/week10/lesson04_flat.cpp"
--8<-- "examples/week10/lesson04_flat.cpp"
```

**Output**:

```text
--8<-- "examples/week10/lesson04_flat.out"
```

## Key takeaways

!!! success "Key takeaways"
    - `stack`, `queue` and `priority_queue` are adaptors over other containers.
    - `pop()` returns void; read `top()`/`front()` first.
    - `priority_queue` is a max-heap by default; use `std::greater<>` for a min-heap.
    - `flat_map`/`flat_set` (C++23) store sorted contiguous data: fast lookup, slower mid insertion.

## Quiz

**Q1.** Why does `std::stack::pop()` return `void`?

??? question "Show answer"
    Returning the removed element by value could throw (during the copy) after the element was already removed, losing it; splitting `top()` and `pop()` keeps the strong guarantee.

**Q2.** How do you make a min-heap with `std::priority_queue`?

??? question "Show answer"
    `std::priority_queue<T, std::vector<T>, std::greater<>>`.

**Q3.** When is `flat_map` a worse choice than `map`?

??? question "Show answer"
    When you do frequent insertions/erasures in a large container (O(n) shifts), or need iterators/references stable across insertions.

