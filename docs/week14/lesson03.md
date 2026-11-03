# Lesson 14.3: Building a thread pool

<span class="stdtag">C++20</span> · about 14 minutes

## Why this matters

Creating a thread per task costs tens of microseconds and unbounded threads thrash the machine. A **thread
pool** creates N workers once and feeds them tasks through a queue. It's the most-used concurrency component
in real systems — and the core of the first capstone. Let's build a small, correct one.

## Design

- A `std::deque` of tasks guarded by a mutex + condition variable (Week 13).
- N `std::jthread` workers loop: wait for a task or stop, run it.
- `submit(f, args...)` wraps the call in a `std::packaged_task`, pushes it, and returns a `std::future`.
- The destructor stops accepting work, drains the queue, and joins.

Because `packaged_task` is move-only and `std::function` requires copyable callables, we hold it via
`std::shared_ptr` (portable everywhere); with C++23 `std::move_only_function` you can store it directly.

!!! note "Why CI doesn't run this one under ThreadSanitizer"
    GCC 14's TSan reports a false "data race" in `std::exception_ptr`'s reference count when an exception
    travels through a future: the count is updated inside the prebuilt (uninstrumented) `libstdc++.so`,
    so TSan can't see its atomics. It's a tooling limitation, not a bug in the pool. The capstone's tests
    run under TSan with Clang.

```cpp title="examples/week14/lesson03.cpp"
--8<-- "examples/week14/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week14/lesson03.out"
```

## Things the simple pool doesn't do

- **Work stealing**: per-worker deques where idle workers steal from busy ones (reduces contention).
- **Priorities, cancellation, back-pressure** (bounded queue).
- **Tasks waiting on other tasks** inside the pool can deadlock if all workers block — a classic trap.

The capstone extends this pool with a bounded queue, statistics, and tests.

## Key takeaways

!!! success "Key takeaways"
    - A thread pool reuses N workers fed by a mutex/condvar queue.
    - `packaged_task` + `future` returns values and exceptions from tasks.
    - Run tasks outside the lock; drain and join on shutdown (member order matters!).
    - Watch for tasks that block on other tasks in the same pool — deadlock.

## Quiz

**Q1.** Why is `workers_` declared last in the class?

??? question "Show answer"
    Members are destroyed in reverse order, so the jthreads join first, while the mutex, condvar and queue they use still exist.

**Q2.** Why wrap `packaged_task` in a `shared_ptr`?

??? question "Show answer"
    `std::function` requires a copyable callable and `packaged_task` is move-only.

**Q3.** How can a pool with 4 workers deadlock?

??? question "Show answer"
    If 4 tasks each wait on futures of tasks still in the queue, no worker is free to run those tasks.

