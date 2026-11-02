# Lesson 14.6: Coroutines II: awaitables and async tasks

<span class="stdtag">C++20</span> · about 14 minutes

## Why this matters

Generators produce values. The bigger win of coroutines is **async I/O**: "read from the socket, then parse,
then write" without callback pyramids. The key is `co_await`, which suspends the coroutine until some
operation finishes and then resumes it with the result. Let's build a tiny single-threaded event loop and a
`Task` type to see how async frameworks work under the hood.

## The awaitable protocol

`co_await x` calls three functions on the awaiter:

| Function | Question it answers |
|---|---|
| `await_ready()` | Is the result already available? If true, don't suspend. |
| `await_suspend(handle)` | We're suspending — who will resume us? (store the handle somewhere) |
| `await_resume()` | Resumed — what's the value of the `co_await` expression? |

## A lazy `Task` and an event loop

In the example, `sleep_ticks(n)` is an awaitable that schedules the current coroutine on a simple event loop
`n` ticks later. `Task<T>` is lazy: it starts when awaited, and when it finishes, its `final_suspend` resumes
the awaiting coroutine via **symmetric transfer** (returning the continuation's handle), which avoids stack
growth in long chains.

```cpp title="examples/week14/lesson06.cpp"
--8<-- "examples/week14/lesson06.cpp"
```

**Output**:

```text
--8<-- "examples/week14/lesson06.out"
```

Notice the output: two "requests" interleave on a single thread — that's concurrency without threads.

## Use a library

Production code should use a proven library (Asio's coroutines, Folly, cppcoro-style libraries, or
`std::execution` in C++26). Writing your own task type is educational but has many subtle lifetime corners.

## Key takeaways

!!! success "Key takeaways"
    - `co_await` uses `await_ready` / `await_suspend` / `await_resume`.
    - A lazy `Task` starts when awaited and resumes its awaiter at `final_suspend`.
    - Symmetric transfer (returning a handle) avoids stack growth in chains of coroutines.
    - Coroutines give concurrency without threads; use a proven library in production.

## Quiz

**Q1.** What does `await_suspend` typically do?

??? question "Show answer"
    Arranges for the suspended coroutine's handle to be resumed later (e.g. registers it with an event loop or I/O completion).

**Q2.** Why is the `Task` lazy (suspend at start)?

??? question "Show answer"
    So the awaiting coroutine can register itself as the continuation before the child runs, avoiding races and wasted work.

**Q3.** In the example, why do requests A and B interleave on one thread?

??? question "Show answer"
    Each suspends at `co_await sleep_ticks`, returning control to the event loop, which resumes whichever timer is due next.

