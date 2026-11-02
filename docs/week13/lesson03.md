# Lesson 13.3: Condition variables and a thread-safe queue

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

A decoder thread produces audio blocks; a player thread consumes them. When the queue is empty the player
should *sleep*, not spin burning a core, and wake the moment a block arrives. That's what condition
variables do — and they have two famous traps.

## The pattern

```cpp
std::unique_lock lock{m};
cv.wait(lock, [&] { return !queue.empty(); });   // ALWAYS wait with a predicate
```

`wait` atomically unlocks the mutex and sleeps; on wake-up it re-locks and re-checks the predicate.

## The two traps

1. **Spurious wakeups**: `wait` may return without a notify. The predicate form loops for you.
2. **Lost wakeups**: if you change the condition *without holding the mutex*, a notify can slip between
   the waiter's check and its sleep. Always modify the shared state under the lock.

```cpp title="examples/week13/lesson03.cpp"
--8<-- "examples/week13/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week13/lesson03.out"
```

## Shutdown

A blocking queue needs a way to say "no more items". The example uses a `closed` flag; C++20's
`condition_variable_any::wait(lock, stop_token, pred)` also wakes on stop requests.

`notify_one` wakes one waiter (one item added); `notify_all` wakes everyone (state change like shutdown).

## Key takeaways

!!! success "Key takeaways"
    - Always `wait` with a predicate — it handles spurious wakeups.
    - Change the shared condition while holding the mutex to avoid lost wakeups.
    - Blocking queues need an explicit close/shutdown path.
    - `condition_variable_any` can wait on a `stop_token` (C++20).

## Quiz

**Q1.** Why must `wait` take a `unique_lock` and not a `lock_guard`?

??? question "Show answer"
    `wait` needs to unlock and re-lock the mutex, which `lock_guard` can't do.

**Q2.** What's a lost wakeup?

??? question "Show answer"
    A notify that happens after the waiter checked the condition but before it went to sleep, so it sleeps forever; prevented by changing state under the mutex.

**Q3.** When is `notify_all` the right choice?

??? question "Show answer"
    When a change matters to all waiters, e.g. shutdown/close.

