# Week 6 programming assignment: A plugin-style effect chain

Design an `Effect` interface (NVI: public non-virtual `process(std::span<float>)` that skips disabled effects;
private virtual `do_process`). Implement `Gain`, `Clip` and `Delay` (a simple fixed delay line).

1. Store effects in `std::vector<std::unique_ptr<Effect>>`.
2. Support `clone()` so a chain can be duplicated.
3. Process an impulse `[1, 0, 0, 0, 0, 0]` through the chain and print the result.
4. No `dynamic_cast` allowed.

??? tip "Reference solution"
    ```cpp title="examples/week06/assignment_solution.cpp"
    --8<-- "examples/week06/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week06/assignment_solution.out"
    ```

