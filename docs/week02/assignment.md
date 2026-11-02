# Week 2 programming assignment: A tiny command-line unit converter

Write a program that converts between units of audio level and time:

- `enum class Unit { ms, samples, seconds }` with a `[[nodiscard]] double convert(double value, Unit from, Unit to, int sample_rate = 48000)` function.
- Overload a `print` function for `double` and for a `struct Result { double value; Unit unit; }`.
- Use `const&` parameters for anything that isn't a cheap scalar.
- Process a fixed list of test conversions in `main` with a range-for loop and print the results.

Compile warning-free. Bonus: use a `switch` with `using enum Unit;`.

??? tip "Reference solution"
    ```cpp title="examples/week02/assignment_solution.cpp"
    --8<-- "examples/week02/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week02/assignment_solution.out"
    ```

