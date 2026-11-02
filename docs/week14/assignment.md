# Week 14 programming assignment: Parallel pipeline with a pool and an SPSC ring

Combine this week's pieces: a producer thread generates 10,000 "audio blocks" (integers) into an
`SpscRing`; a dispatcher thread pops them and submits a processing job (e.g. square modulo 1000) for each to a
`ThreadPool`; gather futures and print the count and checksum, verifying against a sequential computation.
Must be ThreadSanitizer-clean.

??? tip "Reference solution"
    ```cpp title="examples/week14/assignment_solution.cpp"
    --8<-- "examples/week14/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week14/assignment_solution.out"
    ```

