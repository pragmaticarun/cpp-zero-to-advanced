# Lesson 12.5: std::filesystem

<span class="stdtag">C++20</span> · about 10 minutes

## Why this matters

Batch-converting a folder of WAV files, cleaning up old logs, finding every `.json` preset under a
directory — before C++17 these needed POSIX or Win32 calls. `std::filesystem` makes them portable. It also
has a few sharp edges around errors and races that we'll point out.

## Paths

`std::filesystem::path` handles separators and pieces: `p / "sub" / "file.wav"`, `p.filename()`,
`p.stem()`, `p.extension()`, `p.parent_path()`, `p.replace_extension(".flac")`. It's just a string
manipulation type — a path doesn't have to exist.

## Walking directories

`directory_iterator` lists one directory; `recursive_directory_iterator` walks the tree. Iteration order is
**unspecified** — sort if you need determinism.

```cpp title="examples/week12/lesson05.cpp"
--8<-- "examples/week12/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week12/lesson05.out"
```

## Errors

Almost every function has two overloads: one throws `std::filesystem::filesystem_error`, one takes
`std::error_code&` (Week 9). Use the `error_code` form when failure is expected (e.g. "delete if exists").

## The TOCTOU trap

```cpp
if (fs::exists(p)) fs::remove(p);   // another process may delete p in between ("time of check to time of use")
```

Just do the operation and handle the error: `fs::remove(p, ec);`. Filesystems are shared, concurrent state.

## Reading and writing files

`std::ofstream out{path, std::ios::binary}` / `std::ifstream`. Streams don't throw by default — check
`if (!in)` or enable exceptions with `in.exceptions(...)`. For a whole file:
`std::string data{std::istreambuf_iterator<char>{in}, {}};`.

## Key takeaways

!!! success "Key takeaways"
    - `fs::path` composes and dissects paths portably; it doesn't need to exist.
    - Directory iteration order is unspecified; sort when you need determinism.
    - Use `error_code` overloads when failure is normal; avoid check-then-act (TOCTOU) races.
    - Streams don't throw by default — check their state.

## Quiz

**Q1.** What's wrong with `if (fs::exists(p)) fs::remove(p);`?

??? question "Show answer"
    A race: the file can change between the check and the removal; just call `fs::remove(p, ec)` and inspect `ec`.

**Q2.** Does `recursive_directory_iterator` visit files in alphabetical order?

??? question "Show answer"
    Not necessarily — the order is unspecified.

**Q3.** What does `fs::remove` (error_code overload) report for a missing file?

??? question "Show answer"
    It returns false and leaves `ec` clear — a missing file isn't an error for `remove`.

