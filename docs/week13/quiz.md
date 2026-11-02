# Week 13 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 13.1)* What happens if a joinable `std::thread` is destroyed?

??? question "Show answer"
    `std::terminate()` is called.

**Q2.** *(from 13.1)* Can `request_stop()` forcibly stop a thread?

??? question "Show answer"
    No — it only sets a flag; the thread must check its `stop_token` and return.

**Q3.** *(from 13.2)* Is `++counter` on a shared `int` from two threads safe?

??? question "Show answer"
    No — it's a data race (UB); use a mutex or `std::atomic<int>`.

**Q4.** *(from 13.2)* How does `std::scoped_lock{m1, m2}` avoid deadlock?

??? question "Show answer"
    It uses a deadlock-avoidance algorithm (like `std::lock`) to acquire both without holding one while blocking forever on the other.

**Q5.** *(from 13.3)* Why must `wait` take a `unique_lock` and not a `lock_guard`?

??? question "Show answer"
    `wait` needs to unlock and re-lock the mutex, which `lock_guard` can't do.

**Q6.** *(from 13.3)* What's a lost wakeup?

??? question "Show answer"
    A notify that happens after the waiter checked the condition but before it went to sleep, so it sleeps forever; prevented by changing state under the mutex.

**Q7.** *(from 13.4)* What happens to an exception thrown inside a `std::async` task?

??? question "Show answer"
    It's stored in the shared state and rethrown by `get()`.

**Q8.** *(from 13.4)* Why might `std::async(f);` (result ignored) not run concurrently?

??? question "Show answer"
    The temporary future's destructor blocks until the task finishes, so the statement waits right there.

**Q9.** *(from 13.5)* Can a `std::latch` be reused after it reaches zero?

??? question "Show answer"
    No — it's single-use; use `std::barrier` for repeated phases.

**Q10.** *(from 13.5)* What does a barrier's completion function do?

??? question "Show answer"
    Runs once per phase, after all threads arrive and before they're released.

