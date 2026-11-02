# Week 16 programming assignment: Ship a library

Package one of your earlier assignments (e.g. the LRU cache or the config parser) as a library: a namespaced
public header with strong types and `[[nodiscard]]`, a C API wrapper with opaque handles and error codes,
tests, and a CMakeLists.txt with PUBLIC/PRIVATE usage requirements. The reference solution shows the C API
wrapper over the LRU cache, exercised from "C-style" client code.

??? tip "Reference solution"
    ```cpp title="examples/week16/assignment_solution.cpp"
    --8<-- "examples/week16/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week16/assignment_solution.out"
    ```

