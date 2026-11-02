# Week 13: Concurrency I: threads, locks, and synchronization

Your phone has 8 cores; a single-threaded program uses one. This week we learn to use the rest *safely*:
starting threads, protecting shared data, waiting for events, and getting results back. Honest warning:
concurrency bugs are the hardest bugs in software — they hide in testing and appear in production. Every
example here runs under ThreadSanitizer in CI, and you should run yours under it too.

| # | Lesson | Standard | Length |
|---|---|---|---|
| 13.1 | [Threads, jthread, and cooperative cancellation](lesson01.md) | C++20 | 12 min |
| 13.2 | [Data races, mutexes, and deadlock](lesson02.md) | C++20 | 13 min |
| 13.3 | [Condition variables and a thread-safe queue](lesson03.md) | C++20 | 12 min |
| 13.4 | [Futures, promises, async, and packaged_task](lesson04.md) | C++20 | 10 min |
| 13.5 | [Latches, barriers, semaphores, and thread_local](lesson05.md) | C++20 | 10 min |

When you're done with the lessons, take the [week quiz](quiz.md) and the [programming assignment](assignment.md).
