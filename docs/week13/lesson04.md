# Lesson 13.4: Futures, promises, async, and packaged_task

<span class="stdtag">C++20</span> · about 10 minutes

## Why this matters

Threads and mutexes are low-level. Often you just want "compute this in the background and give me the
answer later". A `std::future` is a one-shot channel for a result — or an exception — from another thread.

## `std::async`

```cpp
auto f = std::async(std::launch::async, analyze, file);   // runs on another thread
Report r = f.get();                                        // waits; rethrows if analyze threw
```

Always pass `std::launch::async`: the default policy may run the task lazily on `get()` in the *calling*
thread. And beware: the destructor of a future returned by `std::async` **blocks** until the task finishes —
`std::async(...)` whose result you ignore runs synchronously.

## `promise` and `packaged_task`

A `promise` is the writing end of a future: someone calls `set_value` or `set_exception`. A
`packaged_task` wraps a callable so that calling it fulfils a future — the building block of thread pools
(Week 14).

```cpp title="examples/week13/lesson04.cpp"
--8<-- "examples/week13/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week13/lesson04.out"
```

## Limits

`std::future` has no continuations (`.then`), no composition (`when_all`), and `get()` can only be called
once (use `shared_future` for many readers). For larger async systems look at `std::execution` (C++26,
Week 14) or libraries.

## Key takeaways

!!! success "Key takeaways"
    - A future is a one-shot result channel that also carries exceptions.
    - Use `std::launch::async` explicitly; an ignored `std::async` future blocks in its destructor.
    - `promise` sets a future manually; `packaged_task` ties a callable to a future.
    - `std::future` lacks continuations and composition — bigger systems need more.

## Quiz

**Q1.** What happens to an exception thrown inside a `std::async` task?

??? question "Show answer"
    It's stored in the shared state and rethrown by `get()`.

**Q2.** Why might `std::async(f);` (result ignored) not run concurrently?

??? question "Show answer"
    The temporary future's destructor blocks until the task finishes, so the statement waits right there.

**Q3.** How do several threads read the same result?

??? question "Show answer"
    Convert to `std::shared_future` (`share()`); its `get()` can be called multiple times.

