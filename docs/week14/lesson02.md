# Lesson 14.2: A lock-free single-producer/single-consumer ring buffer

<span class="stdtag">C++20</span> · about 14 minutes

## Why this matters

The audio callback (real-time, can't block) receives samples from the decoder thread. A mutex could block
the callback if the decoder holds it while being descheduled — an audible glitch. The standard answer is a
**single-producer single-consumer (SPSC) lock-free ring buffer**: fixed capacity, no allocation, no locks,
and only acquire/release atomics. It's also the heart of the embedded capstone.

## Design

A fixed array plus two indices: `head` (written only by the consumer) and `tail` (written only by the
producer). Because each index has a single writer, we don't need CAS — just loads and stores with the right
ordering:

- Producer: write the slot, then `tail.store(next, release)` — publishes the element.
- Consumer: `tail.load(acquire)` to see published elements, read the slot, then `head.store(next, release)`
  to hand the slot back.

We keep one slot empty to distinguish "full" from "empty", and use a power-of-two capacity so wrap-around
is a cheap mask.

```cpp title="examples/week14/lesson02.cpp"
--8<-- "examples/week14/lesson02.cpp"
```

**Output**:

```text
--8<-- "examples/week14/lesson02.out"
```

## False sharing

If `head` and `tail` share a cache line, every write by one core invalidates the other core's copy, even
though they touch different variables. Put them on separate cache lines with `alignas(64)` (or
`std::hardware_destructive_interference_size` where available).

## Beyond SPSC

Multi-producer/multi-consumer lock-free queues need CAS and run into the **ABA problem** (a value changes
A→B→A and CAS wrongly succeeds) and safe memory reclamation (hazard pointers, RCU — `std::hazard_pointer`
and `std::rcu` are coming in C++26). Use a well-tested library (e.g. moodycamel, Folly, Boost.Lockfree)
rather than rolling your own.

## Key takeaways

!!! success "Key takeaways"
    - Single-writer indices + acquire/release make an SPSC ring buffer lock-free without CAS.
    - Keep one slot empty to tell full from empty; power-of-two sizes make wrap-around a mask.
    - Separate hot atomics onto different cache lines to avoid false sharing.
    - MPMC lock-free structures face ABA and reclamation problems — use proven libraries.

## Quiz

**Q1.** Why doesn't the SPSC queue need compare-exchange?

??? question "Show answer"
    Each index has exactly one writer thread, so plain atomic stores suffice.

**Q2.** What would happen if the producer stored `tail` before writing the slot?

??? question "Show answer"
    The consumer could see the new tail and read a slot that hasn't been written yet.

**Q3.** What is false sharing?

??? question "Show answer"
    Independent variables on the same cache line causing cache-line ping-pong between cores when written.

