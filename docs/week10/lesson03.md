# Lesson 10.3: Associative and unordered containers

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

"Look up a sample by its name." "Count how many times each word appears." "Keep events sorted by time."
These are the jobs of associative containers. You have two families: tree-based (`map`, `set`), sorted with
O(log n) operations, and hash-based (`unordered_map`, `unordered_set`), unsorted with O(1) average. Knowing
their APIs well — `try_emplace`, `contains`, heterogeneous lookup — avoids a lot of slow, buggy code.

## The `operator[]` trap

```cpp
std::map<std::string, int> counts;
if (counts["drums"] > 0) ...     // WRONG for a lookup: inserts "drums" -> 0 if missing!
```

`operator[]` inserts a default value when the key is missing (and so doesn't work on a `const` map). For
lookups use `find`, `contains` (C++20) or `at` (throws if missing).

## Insertion done right

- `try_emplace(key, args...)` — constructs the value only if the key is absent.
- `insert_or_assign(key, value)` — explicit upsert, tells you which happened.

## Heterogeneous lookup

With `std::map<std::string, int>`, `m.find("drums")` creates a temporary `std::string`. Use a *transparent*
comparator, `std::map<std::string, int, std::less<>>`, and lookups with `std::string_view` or `const char*`
allocate nothing. For unordered containers (C++20) you need a transparent hash *and* `std::equal_to<>`.

```cpp title="examples/week10/lesson03.cpp"
--8<-- "examples/week10/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week10/lesson03.out"
```

## Custom keys

`map` needs `operator<` (or a comparator) — `<=>` from Week 4 provides it. `unordered_map` needs a hash:
specialize `std::hash<Key>` or pass a hasher type. Combine field hashes carefully (the example uses a
simple `boost::hash_combine`-style mix).

## Which one?

| Need | Use |
|---|---|
| Sorted iteration, range queries (`lower_bound`) | `map`/`set` |
| Fastest average lookup, no order needed | `unordered_map`/`unordered_set` |
| Small, mostly-read data | sorted `vector` or `flat_map` (next lesson) |

Node handles (`extract`/`merge`, C++17) move elements between maps — even change a key — without
reallocating.

## Key takeaways

!!! success "Key takeaways"
    - `operator[]` inserts on a miss; use `find`, `contains` or `at` for lookups.
    - Use `try_emplace` and `insert_or_assign` for clear insertion semantics.
    - Transparent comparators/hashes enable lookups by `string_view` without temporaries.
    - Tree containers are ordered (range queries); hash containers are faster on average but unordered.

## Quiz

**Q1.** Why doesn't `counts["x"]` compile on a `const std::map`?

??? question "Show answer"
    `operator[]` may insert, so it's non-const; use `at` or `find`.

**Q2.** What do you need for heterogeneous lookup in `std::unordered_map` (C++20)?

??? question "Show answer"
    A transparent hash (with `is_transparent`) and a transparent equality such as `std::equal_to<>`.

**Q3.** What's the advantage of `extract` + `insert` over erase + insert?

??? question "Show answer"
    The node is reused — no deallocation/allocation and no copy of the value — and you can even modify the key.

