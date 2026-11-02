# Week 10 programming assignment: An LRU cache

Implement `LruCache<Key, Value>` with capacity N:

- `std::optional<Value> get(const Key&)` — returns the value and marks it most-recently used.
- `void put(Key, Value)` — inserts/updates; evicts the least-recently used entry when full.
- Both operations must be O(1) average: use `std::list` for recency order and `std::unordered_map` from key to
  list iterator (this is the classic case where `list`'s stable iterators and `splice` shine).

??? tip "Reference solution"
    ```cpp title="examples/week10/assignment_solution.cpp"
    --8<-- "examples/week10/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week10/assignment_solution.out"
    ```

