# Lesson 13.1: Threads, jthread, and cooperative cancellation

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

Suppose you're decoding 200 audio files. One at a time takes 40 seconds; spread across 8 cores, about 5. A
thread is an independent flow of execution sharing your process's memory. That sharing is the power — and
the danger. Let's start with the mechanics: starting, joining, and stopping threads cleanly.

## `std::thread` and its trap

```cpp
std::thread t{work};
// if we forget t.join() and t goes out of scope -> std::terminate()!
```

A joinable `std::thread` destroyed without `join()` or `detach()` calls `std::terminate`. And `detach()`
is almost always wrong: the thread may outlive the data it uses.

## `std::jthread` (C++20): use this by default

`jthread` joins automatically in its destructor, *and* carries a `std::stop_token` so you can ask it to stop.
Cancellation is **cooperative**: the thread checks `stop_requested()` and exits on its own. There's no safe
way to kill a thread from outside.

```cpp title="examples/week13/lesson01.cpp"
--8<-- "examples/week13/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week13/lesson01.out"
```

## Arguments are copied

`std::thread{f, x}` copies `x` into the thread's storage. To pass a reference use `std::ref(x)` — and make
sure `x` outlives the thread. Passing a pointer or reference to a local that goes out of scope is the
classic dangling bug.

## How many threads?

`std::thread::hardware_concurrency()` hints at the number of hardware threads (may return 0 if unknown).
More threads than cores for CPU-bound work just adds context switches.

## Key takeaways

!!! success "Key takeaways"
    - A joinable `std::thread` that's destroyed calls `std::terminate`; prefer `std::jthread`.
    - `jthread` auto-joins and supports cooperative cancellation via `stop_token`.
    - Thread arguments are copied; use `std::ref` deliberately and mind lifetimes.
    - Avoid `detach()`; don't run more CPU-bound threads than cores.

## Quiz

**Q1.** What happens if a joinable `std::thread` is destroyed?

??? question "Show answer"
    `std::terminate()` is called.

**Q2.** Can `request_stop()` forcibly stop a thread?

??? question "Show answer"
    No — it only sets a flag; the thread must check its `stop_token` and return.

**Q3.** Why is `std::thread t{f, std::ref(local)}; t.detach();` dangerous?

??? question "Show answer"
    The thread may still use `local` after the enclosing function returns — a dangling reference.

