# Week 12 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 12.1)* What's `sizeof(std::unique_ptr<int>)` on a typical 64-bit platform?

??? question "Show answer"
    8 bytes — the same as a raw pointer (with the default deleter).

**Q2.** *(from 12.1)* How should a function that only reads a `Codec` take it?

??? question "Show answer"
    By `const Codec&` (or `const Codec*` if null is allowed), not by smart pointer.

**Q3.** *(from 12.2)* Is `shared_ptr` thread-safe?

??? question "Show answer"
    The reference counting is (atomic); accessing the pointed-to object or assigning to the same shared_ptr instance from several threads is not (use `std::atomic<std::shared_ptr<T>>` for the latter).

**Q4.** *(from 12.2)* How does `weak_ptr` break a cycle?

??? question "Show answer"
    It doesn't contribute to the strong count, so the objects can be destroyed when external owners go away.

**Q5.** *(from 12.3)* Why can't you pass `std::vector<int, MyAlloc<int>>` to a function taking `const std::vector<int>&`?

??? question "Show answer"
    The allocator is a template parameter, so they're different types.

**Q6.** *(from 12.3)* What does `deallocate` do on a `monotonic_buffer_resource`?

??? question "Show answer"
    Nothing — memory is only reclaimed when the resource is released or destroyed.

**Q7.** *(from 12.4)* What happens if you write `std::format("{:d}", std::string{"x"})`?

??? question "Show answer"
    A compile-time error: the format string is checked against the argument types.

**Q8.** *(from 12.4)* Why can `std::endl` make output slow?

??? question "Show answer"
    It flushes the stream every time; in a loop that defeats buffering.

**Q9.** *(from 12.5)* What's wrong with `if (fs::exists(p)) fs::remove(p);`?

??? question "Show answer"
    A race: the file can change between the check and the removal; just call `fs::remove(p, ec)` and inspect `ec`.

**Q10.** *(from 12.5)* Does `recursive_directory_iterator` visit files in alphabetical order?

??? question "Show answer"
    Not necessarily — the order is unspecified.

**Q11.** *(from 12.6)* Why does `std::chrono::seconds s = 1500ms;` not compile?

??? question "Show answer"
    The conversion would lose information (truncate), so it must be explicit.

**Q12.** *(from 12.6)* Which clock should measure how long a function takes?

??? question "Show answer"
    `std::chrono::steady_clock` — it's monotonic and unaffected by wall-clock adjustments.

**Q13.** *(from 12.7)* Why is `rand() % 6` a poor die?

??? question "Show answer"
    `rand()` is low-quality and `%` introduces bias when RAND_MAX+1 isn't a multiple of 6; use `std::uniform_int_distribution` with a good engine.

**Q14.** *(from 12.7)* What is `std::numeric_limits<float>::min()`?

??? question "Show answer"
    The smallest positive normalized float (~1.18e-38), not the most negative value — that's `lowest()`.

