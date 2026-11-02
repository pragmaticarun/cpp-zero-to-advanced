# Week 11 programming assignment: A log analysis pipeline

Given lines like `"12:00:01 WARN disk 91%"`, write range pipelines (no raw `for` loops except for printing) to:

1. Count lines per level (`INFO`, `WARN`, `ERROR`) using `std::ranges::count_if`.
2. Collect the messages of the first 2 `ERROR` lines into a `std::vector<std::string>` with `std::ranges::to`.
3. Print the line numbers (1-based) of all `WARN` lines using `views::enumerate`.

??? tip "Reference solution"
    ```cpp title="examples/week11/assignment_solution.cpp"
    --8<-- "examples/week11/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week11/assignment_solution.out"
    ```

