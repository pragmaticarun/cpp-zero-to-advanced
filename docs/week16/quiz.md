# Week 16 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 16.1)* Why must `dsp_mixer_process` catch all exceptions?

??? question "Show answer"
    Unwinding through C frames (or into another language's runtime) is undefined behaviour.

**Q2.** *(from 16.1)* How does a C callback get access to the caller's state?

??? question "Show answer"
    Through a `void* user_data` parameter passed back to the callback.

**Q3.** *(from 16.2)* Why avoid dynamic allocation after startup on an MCU?

??? question "Show answer"
    Fragmentation and non-deterministic timing can cause failures or missed deadlines.

**Q4.** *(from 16.2)* Why did C++20 deprecate `reg |= bit` on a volatile?

??? question "Show answer"
    It looks atomic but is a separate read and write; writing it out makes the two accesses explicit.

**Q5.** *(from 16.3)* When is `std::variant` + `std::visit` better than a virtual-function hierarchy?

??? question "Show answer"
    When the set of types is closed and known, and you want to add operations easily without touching the types.

**Q6.** *(from 16.3)* What bug does `weak_ptr` prevent in the observer?

??? question "Show answer"
    Calling a listener that has been destroyed (dangling callback).

**Q7.** *(from 16.4)* Why is `void f(bool fast, bool safe)` a weak signature?

??? question "Show answer"
    Call sites like `f(true, false)` are unreadable and easy to swap; use enums or strong types.

**Q8.** *(from 16.4)* What does an inline namespace give you for versioning?

??? question "Show answer"
    Its contents are accessible from the enclosing namespace by default, while older versions remain addressable explicitly (and mangled names differ per version).

**Q9.** *(from 16.5)* What does `^^T` produce in C++26?

??? question "Show answer"
    A `std::meta::info` value representing the type `T` at compile time.

**Q10.** *(from 16.5)* How do C++26 contracts differ from `assert`?

??? question "Show answer"
    They're part of the function declaration (visible to callers and tools) and have standardized evaluation semantics selectable at build time.

