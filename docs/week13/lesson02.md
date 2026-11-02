# Lesson 13.2: Data races, mutexes, and deadlock

<span class="stdtag">C++20</span> · about 13 minutes

## Why this matters

Two threads each add 1 to a counter a million times. Expected: 2,000,000. Actual: maybe 1,213,407 — and
different every run. That's a **data race**: two threads access the same memory, at least one writes, and
nothing orders them. In C++ a data race isn't just a wrong number — it's undefined behaviour.

## The wrong way

!!! bug "Deliberately buggy"
    CI runs this under `-fsanitize=thread` and checks the sanitizer reports the bug.

```cpp title="examples/week13/lesson02_race.cpp"
--8<-- "examples/week13/lesson02_race.cpp"
```

`++counter` is read-modify-write; two threads interleave and lose updates. ThreadSanitizer flags this
immediately (CI runs this example under TSan and checks it's reported).

## Mutexes and RAII locks

```cpp
std::mutex m;
{ std::lock_guard lock{m}; ++counter; }   // unlocked automatically, even on exceptions
```

Never call `m.lock()`/`m.unlock()` by hand. Use `lock_guard` (simple), `unique_lock` (movable, can unlock
early, needed for condition variables), `scoped_lock` (locks several mutexes at once without deadlock).

```cpp title="examples/week13/lesson02.cpp"
--8<-- "examples/week13/lesson02.cpp"
```

**Output**:

```text
--8<-- "examples/week13/lesson02.out"
```

## Deadlock

Thread A locks `m1` then waits for `m2`; thread B locks `m2` then waits for `m1`. Forever. Fixes: always
lock in a consistent global order, or lock both at once with `std::scoped_lock{m1, m2}`, and never call
unknown code (callbacks) while holding a lock.

## Readers–writer locks and one-time init

`std::shared_mutex` lets many readers hold `shared_lock` at once while writers take `unique_lock`. Useful
for read-mostly data (but measure — it's heavier than a plain mutex). `std::call_once` and function-local
`static` variables give thread-safe lazy initialization.

!!! warning "Pitfall"
    Keep critical sections short. Holding a lock while doing I/O or calling a callback serializes your
    program and invites deadlock.

## Key takeaways

!!! success "Key takeaways"
    - A data race (unsynchronized access with at least one write) is undefined behaviour.
    - Protect shared data with a mutex and RAII locks; never lock/unlock by hand.
    - Use `std::scoped_lock` for multiple mutexes, or a consistent lock order, to avoid deadlock.
    - `shared_mutex` for read-mostly data; `call_once`/static locals for one-time init.

## Quiz

**Q1.** Is `++counter` on a shared `int` from two threads safe?

??? question "Show answer"
    No — it's a data race (UB); use a mutex or `std::atomic<int>`.

**Q2.** How does `std::scoped_lock{m1, m2}` avoid deadlock?

??? question "Show answer"
    It uses a deadlock-avoidance algorithm (like `std::lock`) to acquire both without holding one while blocking forever on the other.

**Q3.** Why avoid calling user callbacks while holding a lock?

??? question "Show answer"
    The callback might take another lock (deadlock risk) or be slow, serializing other threads.

