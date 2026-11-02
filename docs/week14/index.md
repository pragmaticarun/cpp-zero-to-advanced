# Week 14: Concurrency II: atomics, lock-free code, thread pools, and coroutines

Last week used locks. This week goes underneath them — atomics and the C++ memory model — then builds two
real components (a lock-free single-producer/single-consumer queue and a thread pool, both feeding the
capstones), and finishes with coroutines, C++20's machinery for writing asynchronous code that reads like
sequential code. This is the hardest week of the course. Go slowly, and lean on ThreadSanitizer.

| # | Lesson | Standard | Length |
|---|---|---|---|
| 14.1 | [Atomics and the memory model](lesson01.md) | C++20 | 15 min |
| 14.2 | [A lock-free single-producer/single-consumer ring buffer](lesson02.md) | C++20 | 14 min |
| 14.3 | [Building a thread pool](lesson03.md) | C++20 | 14 min |
| 14.4 | [Parallel algorithms and a preview of std::execution](lesson04.md) | C++20 | 10 min |
| 14.5 | [Coroutines I: the machinery, and writing a generator](lesson05.md) | C++20 | 15 min |
| 14.6 | [Coroutines II: awaitables and async tasks](lesson06.md) | C++20 | 14 min |

When you're done with the lessons, take the [week quiz](quiz.md) and the [programming assignment](assignment.md).
