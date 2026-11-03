# Capstone A: A concurrent task library with a CLI

## The problem

You have a batch of jobs — say, checksumming files or rendering audio stems. You want a reusable library
that runs them on N threads, returns results through futures, propagates exceptions, applies
**back-pressure** (a bounded queue, so a fast producer can't exhaust memory), reports statistics, and shuts
down cleanly. Then a small command-line tool on top.

## Requirements

1. `ThreadPool(threads, max_queue)` — validates arguments.
2. `submit(f, args...)` → `std::future<R>`; blocks while the queue is full; throws after shutdown.
3. `try_submit(...)` → `std::optional<std::future<R>>`; never blocks.
4. Exceptions inside tasks reach the caller via `future::get()`; the pool keeps running.
5. `wait_idle()` waits until all submitted work is done.
6. `shutdown(drain)` finishes queued work; `shutdown(discard)` drops it (futures report `broken_promise`).
7. `stats()` returns submitted / completed / failed / rejected counts.
8. Tests pass under ThreadSanitizer.

## The library

```cpp title="examples/capstone/threadpool.hpp"
--8<-- "examples/capstone/threadpool.hpp"
```

Design notes:

- **Three condition variables**: `not_empty_` (workers wait for jobs), `not_full_` (producers wait for
  space), `idle_` (`wait_idle`). Separate CVs avoid waking the wrong kind of waiter.
- Jobs run **outside the lock**.
- A task's exception is counted (for `stats().failed`) and rethrown into its `packaged_task`, which stores
  it in the future — so worker threads never see it.
- `shutdown` is idempotent and called from the destructor (RAII).

## Tests

```cpp title="examples/capstone/threadpool_tests.cpp"
--8<-- "examples/capstone/threadpool_tests.cpp"
```

**Output**:

```text
--8<-- "examples/capstone/threadpool_tests.out"
```

## The CLI

`taskrun [--threads N] [--jobs M] [--queue Q]` computes a CPU-bound job set and prints a summary. With no
arguments it uses defaults (which is how the checker runs it).

```cpp title="examples/capstone/threadpool_cli.cpp"
--8<-- "examples/capstone/threadpool_cli.cpp"
```

**Output**:

```text
--8<-- "examples/capstone/threadpool_cli.out"
```

## Extensions

- Work stealing with per-worker deques.
- Task priorities, or cancellation with `std::stop_token`.
- Replace `std::function` with `std::move_only_function` (C++23) to avoid the `shared_ptr`.
- Expose the pool as a `std::execution` scheduler (C++26, via stdexec).
