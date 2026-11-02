# Week 1 programming assignment: A WAV header inspector

Let's put the week together. A WAV file starts with a 44-byte header. You'll write a program that builds a
header for given parameters into a byte array and then *parses it back*, printing the fields.

Requirements:

1. Use fixed-width types (`std::uint16_t`, `std::uint32_t`) for every field.
2. Write little-endian values byte-by-byte with shifts (don't `memcpy` structs — padding and endianness
   make that non-portable).
3. Compute `byte_rate = sample_rate * channels * bits/8` using `constexpr` where possible.
4. Compile warning-free with `-Wall -Wextra -Wpedantic`.

Don't worry if the shifting feels unfamiliar: we cover bit operations properly in Week 3. Peek at the
solution if you get stuck — that's part of learning.

???+ example "Starter code"
    ```cpp title="examples/week01/assignment_starter.cpp"
    --8<-- "examples/week01/assignment_starter.cpp"
    ```

??? tip "Reference solution"
    ```cpp title="examples/week01/assignment_solution.cpp"
    --8<-- "examples/week01/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week01/assignment_solution.out"
    ```

