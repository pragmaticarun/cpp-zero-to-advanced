# Week 3 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 3.1)* Inside `void f(int a[10])`, what is `sizeof(a)` on a 64-bit system?

??? question "Show answer"
    8 — the parameter is actually `int*`; the 10 is ignored.

**Q2.** *(from 3.1)* Does `std::span` own its elements?

??? question "Show answer"
    No. It is a non-owning view (pointer + size). The underlying storage must outlive the span.

**Q3.** *(from 3.2)* If `int a[4]` starts at address 1000 and `sizeof(int)==4`, what address is `a + 3`?

??? question "Show answer"
    1012 — arithmetic is in units of elements.

**Q4.** *(from 3.2)* Which of these can you do with `const char* s`: `s = other;` / `*s = 'x';`?

??? question "Show answer"
    `s = other;` is fine (re-pointing). `*s = 'x';` is an error (the pointee is const).

**Q5.** *(from 3.3)* What's wrong with `int* p = new int[10]; delete p;`?

??? question "Show answer"
    Memory from `new[]` must be released with `delete[]`; using `delete` is undefined behaviour.

**Q6.** *(from 3.3)* Why can't you rely on UB 'just crashing'?

??? question "Show answer"
    The standard imposes no requirements; the optimizer may assume UB is impossible and transform surrounding code, so the effect can be anything, including silently wrong results.

**Q7.** *(from 3.4)* What is `sizeof("abc")`?

??? question "Show answer"
    4: three characters plus the terminating `\0`.

**Q8.** *(from 3.4)* Why is `std::string_view` a good parameter type but a risky member/return type?

??? question "Show answer"
    As a parameter it avoids copies and accepts any string type, and the argument outlives the call. As a return/member it may outlive the characters it views, producing a dangling view.

**Q9.** *(from 3.5)* How do you extract bits 2..4 (3 bits) of `x`?

??? question "Show answer"
    `(x >> 2) & 0b111`.

**Q10.** *(from 3.5)* What is the type and value of `~std::uint8_t{0}`?

??? question "Show answer"
    `int`, value `-1` (all bits set), due to integer promotion before `~`.

