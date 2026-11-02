# Lesson 3.3: Dynamic memory and a first map of undefined behaviour

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

Sometimes you don't know until run time how much memory you need — a frame whose size comes from a
video header, say. That memory comes from the *heap*. C++ lets you manage it by hand with `new` and
`delete`... and this lesson is mostly about why you almost never should. Seeing the failure modes once
will make you appreciate RAII and smart pointers in the coming weeks.

## Stack vs heap

- **Stack** (automatic storage): local variables. Allocation is just moving a pointer — extremely fast —
  and cleanup is automatic at the end of scope. But it's limited (often 1–8 MB per thread) and sizes are
  fixed at compile time.
- **Heap** (dynamic storage): `new` asks the allocator for memory at run time. You decide when it's freed.

```cpp
int* one = new int{5};        // allocate one int
delete one;                   // free it

int* many = new int[n]{};     // allocate n ints, zeroed
delete[] many;                // arrays need delete[]
```

## Four ways manual memory goes wrong

1. **Leak**: forget to `delete` (or an early `return`/exception skips it).
2. **Double free**: `delete` the same pointer twice.
3. **Use-after-free**: use memory after deleting it.
4. **Mismatch**: `new[]` with `delete` (or `malloc` with `delete`).

The last three are **undefined behaviour**.

## What "undefined behaviour" really means

UB doesn't mean "crashes" or "gives a random value". It means **the standard places no requirements on
the program at all**. The optimizer assumes UB never happens and transforms code accordingly. So a
single out-of-bounds read can make an unrelated `if` vanish. Common sources you've met so far:

- signed integer overflow, out-of-bounds access, null/dangling dereference,
- reading uninitialized variables, data races (Week 13), violating aliasing rules (Week 16).

We keep a full catalogue in Lesson 9.5.

## The fix: let objects own memory

Here's the modern answer. You rarely write `new` at all:

```cpp title="examples/week03/lesson03.cpp"
--8<-- "examples/week03/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week03/lesson03.out"
```

`std::vector` and `std::unique_ptr` free their memory automatically when they go out of scope — even if
an exception is thrown. That's RAII, the heart of Week 4.

## Tools that catch memory bugs

Compile with **AddressSanitizer** while developing:

```bash
g++ -std=c++20 -g -fsanitize=address,undefined bug.cpp && ./a.out
```

ASan reports use-after-free, double free, out-of-bounds and leaks with a stack trace. Here's a program
with a deliberate use-after-free. Our checker runs it under ASan in CI to make sure ASan really catches it:

!!! bug "Deliberately buggy"
    CI runs this under `-fsanitize=address` and checks the sanitizer reports the bug.

```cpp title="examples/week03/lesson03_uaf.cpp"
--8<-- "examples/week03/lesson03_uaf.cpp"
```

ASan prints something like `ERROR: AddressSanitizer: heap-use-after-free ... READ of size 4`. Android
supports ASan and HWASan too (HWASan is the recommended one on arm64).

!!! warning "Honest note"
    Valgrind and sanitizers find bugs *in the code paths you execute*. They're not proofs. Combine them
    with tests (Week 15) and with designs where ownership is obvious.

## Key takeaways

!!! success "Key takeaways"
    - Stack allocation is fast and automatic; heap allocation is flexible but must be freed.
    - Manual `new`/`delete` invites leaks, double frees, use-after-free and mismatched `delete[]`.
    - UB means no requirements at all; the optimizer assumes it never happens.
    - Let `std::vector` / `std::unique_ptr` own memory, and develop with `-fsanitize=address,undefined`.

## Quiz

**Q1.** What's wrong with `int* p = new int[10]; delete p;`?

??? question "Show answer"
    Memory from `new[]` must be released with `delete[]`; using `delete` is undefined behaviour.

**Q2.** Why can't you rely on UB 'just crashing'?

??? question "Show answer"
    The standard imposes no requirements; the optimizer may assume UB is impossible and transform surrounding code, so the effect can be anything, including silently wrong results.

**Q3.** Which tool reports heap-use-after-free with a stack trace?

??? question "Show answer"
    AddressSanitizer (`-fsanitize=address`), or HWASan on arm64 Android; also Valgrind's memcheck.

