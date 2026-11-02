# Week 15 programming assignment: Harden and test a parser

Take a small key=value packet parser that reads lengths from untrusted bytes, write table-driven tests
including malicious inputs (truncated, oversized lengths, negative values), and make it safe using
`std::span`, `std::in_range` and `std::expected`. Run under ASan+UBSan. Bonus: write a libFuzzer entry point
(`LLVMFuzzerTestOneInput`) for it.

??? tip "Reference solution"
    ```cpp title="examples/week15/assignment_solution.cpp"
    --8<-- "examples/week15/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week15/assignment_solution.out"
    ```

