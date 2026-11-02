# Week 15 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 15.1)* What does `PUBLIC` mean in `target_include_directories(dsp PUBLIC include)`?

??? question "Show answer"
    The include directory is used to build `dsp` *and* propagates to targets that link `dsp`.

**Q2.** *(from 15.1)* Name two advantages of modules over headers.

??? question "Show answer"
    Faster builds (parsed once), no macro leakage, explicit export control, less ODR fragility.

**Q3.** *(from 15.2)* Why can't C code call an overloaded C++ function directly?

??? question "Show answer"
    C++ mangles parameter types into symbol names; C expects plain names. Use `extern "C"` wrappers (which can't be overloaded).

**Q4.** *(from 15.2)* Is adding a private member to a class in a shared library's header ABI-compatible?

??? question "Show answer"
    No — it changes the object's size/layout, breaking binaries compiled against the old header.

**Q5.** *(from 15.3)* Which sanitizer finds a data race?

??? question "Show answer"
    ThreadSanitizer (`-fsanitize=thread`).

**Q6.** *(from 15.3)* Can ASan and TSan be combined in one build?

??? question "Show answer"
    No — they're incompatible; use separate builds.

**Q7.** *(from 15.4)* Why might a benchmark of `for (...) s += x;` report 0 ns?

??? question "Show answer"
    If `s` is unused the optimizer removes the loop entirely.

**Q8.** *(from 15.4)* What does PGO do?

??? question "Show answer"
    Uses profiles from representative runs to guide inlining, layout and branch decisions.

**Q9.** *(from 15.5)* Why is iterating a `std::list` slower than a `std::vector` of the same size?

??? question "Show answer"
    List nodes are scattered in memory, so each step is a likely cache miss; vector elements are contiguous and prefetched.

**Q10.** *(from 15.5)* What is `sizeof(struct { char a; double b; char c; })` on a typical 64-bit ABI?

??? question "Show answer"
    24 bytes due to padding for 8-byte alignment of `double`.

**Q11.** *(from 15.6)* What does `-D_GLIBCXX_ASSERTIONS` do?

??? question "Show answer"
    Enables libstdc++ precondition checks, e.g. trapping on out-of-bounds `vector::operator[]`.

**Q12.** *(from 15.6)* Why is `-1 < 3u` false?

??? question "Show answer"
    -1 converts to a huge unsigned value; use `std::cmp_less(-1, 3u)` which compares mathematically.

