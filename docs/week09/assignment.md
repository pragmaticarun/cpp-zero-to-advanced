# Week 9 programming assignment: A robust config parser

Parse lines of the form `key=value` into a `Config { int sample_rate; int channels; std::string device; }`.

- Return `std::expected<Config, ConfigError>` where `ConfigError` holds a line number and a message.
- Unknown keys, missing `=`, non-numeric numbers, out-of-range values and missing required keys are errors.
- Use `std::from_chars` (no exceptions in the parser).
- Print the result for one valid and three invalid inputs.

??? tip "Reference solution"
    ```cpp title="examples/week09/assignment_solution.cpp"
    --8<-- "examples/week09/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week09/assignment_solution.out"
    ```

