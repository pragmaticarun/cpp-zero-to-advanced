# Week 11 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 11.1)* What's the complexity of `nth_element`?

??? question "Show answer"
    O(n) on average.

**Q2.** *(from 11.1)* Why is `[](int a, int b){ return a <= b; }` a broken comparator?

??? question "Show answer"
    It's not irreflexive (`comp(a, a)` is true), so it's not a strict weak ordering; `std::sort` may misbehave or read out of bounds.

**Q3.** *(from 11.2)* What's wrong with `std::accumulate(v.begin(), v.end(), 0)` for `std::vector<double>`?

??? question "Show answer"
    The accumulator is `int`, so each partial sum is converted to int — the result is truncated.

**Q4.** *(from 11.2)* Why must you sort before `std::unique` to remove all duplicates?

??? question "Show answer"
    `unique` only collapses consecutive equal elements.

**Q5.** *(from 11.3)* When does the work in `takes | views::filter(f) | views::transform(g)` happen?

??? question "Show answer"
    Lazily, element by element, as you iterate the resulting view — nothing is computed when the pipeline is built.

**Q6.** *(from 11.3)* How do you turn a view into a `std::vector` in C++23?

??? question "Show answer"
    `view | std::ranges::to<std::vector>()`.

**Q7.** *(from 11.4)* What does `std::exchange(x, 0)` return?

??? question "Show answer"
    The old value of `x`; `x` is set to 0.

**Q8.** *(from 11.4)* Why is `std::ref(n)` needed in `std::bind_front(bump, std::ref(n))`?

??? question "Show answer"
    `bind_front` stores copies of its arguments; `std::ref` stores a reference wrapper so `bump` modifies the original `n`.

**Q9.** *(from 11.5)* What happens at `co_yield a;`?

??? question "Show answer"
    The generator produces `a` to the consumer and suspends; it resumes from that point when the consumer asks for the next value.

**Q10.** *(from 11.5)* Why is `std::generator<int> g(const std::string& s)` risky?

??? question "Show answer"
    The coroutine may outlive the referenced argument (e.g. a temporary), leaving a dangling reference when resumed.

