# Week 13 programming assignment: Parallel file checksum

Compute a checksum (sum of bytes mod 2^32) of 64 simulated "files" (vectors of bytes generated
deterministically) using a fixed number of worker threads pulling indices from a shared work queue. Use a
`std::latch` to start all workers simultaneously, a mutex-protected result map, and print results in index
order plus the grand total. Must be TSan-clean and give the same output as a sequential computation.

??? tip "Reference solution"
    ```cpp title="examples/week13/assignment_solution.cpp"
    --8<-- "examples/week13/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week13/assignment_solution.out"
    ```

