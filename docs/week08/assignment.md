# Week 8 programming assignment: A typed event dispatcher

Build `Dispatcher` that lets callers subscribe handlers for different event *types*:

```cpp
d.on<KeyPressed>([](const KeyPressed& e) { ... });
d.emit(KeyPressed{'a'});
```

Requirements: constrain events with a concept `Event` (must be copyable and have a static `name`),
store handlers type-erased in a `std::unordered_map<std::type_index, std::vector<std::function<void(const void*)>>>`,
and print how many handlers ran per emit.

??? tip "Reference solution"
    ```cpp title="examples/week08/assignment_solution.cpp"
    --8<-- "examples/week08/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week08/assignment_solution.out"
    ```

