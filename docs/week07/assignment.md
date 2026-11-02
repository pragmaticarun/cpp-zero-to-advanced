# Week 7 programming assignment: A generic binary serializer

Write `template <typename... Ts> std::vector<std::uint8_t> pack(const Ts&... values)` that serializes every
argument in order: integers big-endian, `bool` as one byte, floating-point via `std::bit_cast`, `std::string`
as a 16-bit length then bytes. Also write `std::string hex(const std::vector<std::uint8_t>&)`.

Unsupported types must be a compile-time error with a readable message.

???+ example "Starter code"
    ```cpp title="examples/week07/assignment_starter.cpp"
    --8<-- "examples/week07/assignment_starter.cpp"
    ```

??? tip "Reference solution"
    ```cpp title="examples/week07/assignment_solution.cpp"
    --8<-- "examples/week07/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week07/assignment_solution.out"
    ```

