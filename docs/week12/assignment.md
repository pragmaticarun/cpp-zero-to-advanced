# Week 12 programming assignment: A media library scanner

Write a tool that scans a directory tree for audio files (`.wav`, `.flac`, `.mp3`), and prints a report:
count per extension, total size, and the 3 largest files — formatted as an aligned table with `std::println`.

Create a test directory under `fs::temp_directory_path()` with a few files of known sizes, run the scan, then
remove it. Use `error_code` overloads for cleanup, and sort results for deterministic output.

??? tip "Reference solution"
    ```cpp title="examples/week12/assignment_solution.cpp"
    --8<-- "examples/week12/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week12/assignment_solution.out"
    ```

