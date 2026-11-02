# Week 14 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 14.1)* Why might `ready.store(true, relaxed)` be insufficient for publishing `data`?

??? question "Show answer"
    Relaxed provides no ordering of other memory, so the consumer may see `ready == true` but a stale `data`.

**Q2.** *(from 14.1)* Why does `compare_exchange_weak` sit in a loop?

??? question "Show answer"
    It can fail spuriously and fails when another thread changed the value; on failure it updates `expected`, so you retry.

**Q3.** *(from 14.2)* Why doesn't the SPSC queue need compare-exchange?

??? question "Show answer"
    Each index has exactly one writer thread, so plain atomic stores suffice.

**Q4.** *(from 14.2)* What would happen if the producer stored `tail` before writing the slot?

??? question "Show answer"
    The consumer could see the new tail and read a slot that hasn't been written yet.

**Q5.** *(from 14.3)* Why is `workers_` declared last in the class?

??? question "Show answer"
    Members are destroyed in reverse order, so the jthreads join first, while the mutex, condvar and queue they use still exist.

**Q6.** *(from 14.3)* Why wrap `packaged_task` in a `shared_ptr`?

??? question "Show answer"
    `std::function` requires a copyable callable and `packaged_task` is move-only.

**Q7.** *(from 14.4)* Why might `std::reduce` give a slightly different floating-point sum than `std::accumulate`?

??? question "Show answer"
    It may group and reorder additions, and FP addition isn't associative.

**Q8.** *(from 14.4)* Can you lock a mutex inside a `par_unseq` lambda?

??? question "Show answer"
    No — vectorized execution may interleave iterations on one thread, so locking can deadlock; it's disallowed.

**Q9.** *(from 14.5)* What makes a function a coroutine?

??? question "Show answer"
    Using `co_await`, `co_yield` or `co_return` in its body.

**Q10.** *(from 14.5)* Why does our generator use `suspend_always` for `initial_suspend`?

??? question "Show answer"
    So the body doesn't run until the caller asks for the first value (lazy).

**Q11.** *(from 14.6)* What does `await_suspend` typically do?

??? question "Show answer"
    Arranges for the suspended coroutine's handle to be resumed later (e.g. registers it with an event loop or I/O completion).

**Q12.** *(from 14.6)* Why is the `Task` lazy (suspend at start)?

??? question "Show answer"
    So the awaiting coroutine can register itself as the continuation before the child runs, avoiding races and wasted work.

