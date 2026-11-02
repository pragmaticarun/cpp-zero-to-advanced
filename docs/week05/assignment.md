# Week 5 programming assignment: A move-aware audio clip

Build `class Clip` that owns samples (`std::vector<float>`), a name (`std::string`) and an id.

1. Follow the Rule of Zero for storage — but add *instrumentation*: a static counter of copies and moves
   using a small member type with custom copy/move that increments counters (so `Clip` itself still writes no
   special members).
2. `static Clip make_sine(std::string name, float freq, int n)` returning by value.
3. A `Playlist` that stores clips in a `std::vector<Clip>` via a sink `add(Clip c)`.
4. Show (by printing counters) that building a playlist of 3 clips performs **zero** copies.

??? tip "Reference solution"
    ```cpp title="examples/week05/assignment_solution.cpp"
    --8<-- "examples/week05/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week05/assignment_solution.out"
    ```

