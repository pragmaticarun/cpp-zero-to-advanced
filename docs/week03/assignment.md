# Week 3 programming assignment: A bit-packed sensor record

A sensor sends 32-bit records: bits 0–11 are a temperature reading (unsigned, 0.1°C steps with an offset of
-40°C), bits 12–19 humidity (percent), bits 20–27 a sensor id, bits 28–31 flags.

1. Write `constexpr std::uint32_t pack(...)` and `Record unpack(std::uint32_t)`.
2. Take a `std::span<const std::uint32_t>` of records and print each one.
3. Report how many records have flag bit 0 set, using `std::popcount` or masks.
4. No raw `new`, no C strings, no `reinterpret_cast`.

??? tip "Reference solution"
    ```cpp title="examples/week03/assignment_solution.cpp"
    --8<-- "examples/week03/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week03/assignment_solution.out"
    ```

