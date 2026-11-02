# Week 9: Error handling and undefined behaviour

Every real program fails: files are missing, packets are corrupt, memory runs out. This week compares C++'s
error-handling tools — exceptions, `std::optional`, `std::expected`, error codes, assertions — and gives
you a rule for choosing. We end with a catalogue of undefined behaviour, the class of bug that makes C++
uniquely dangerous, and the tools that catch it.

| # | Lesson | Standard | Length |
|---|---|---|---|
| 9.1 | [Exceptions: throw, try, catch, and stack unwinding](lesson01.md) | C++20 | 11 min |
| 9.2 | [Exception safety guarantees and noexcept](lesson02.md) | C++20 | 11 min |
| 9.3 | [std::optional and std::variant](lesson03.md) | C++23 | 11 min |
| 9.4 | [std::expected, error codes, and choosing a strategy](lesson04.md) | C++23 | 12 min |
| 9.5 | [Assertions, contracts preview, and the undefined behaviour catalogue](lesson05.md) | C++23 | 14 min |

When you're done with the lessons, take the [week quiz](quiz.md) and the [programming assignment](assignment.md).
