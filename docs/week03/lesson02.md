# Lesson 3.2: Pointers: addresses, arithmetic, and const

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

Pointers have a scary reputation, but the idea is simple: a pointer is a variable that holds the *address*
of another object. Android's NDK APIs, every C library, and hardware registers all speak in pointers, so
you need to be fluent. Let's build the picture step by step.

## The idea

```cpp
int level = 42;
int* p = &level;   // p holds the address of level
*p = 7;            // dereference: "the object p points to" -> level is now 7
```

Draw it as a box (`level`, containing 42) and an arrow (`p`) pointing at it. Unlike a reference, a
pointer can be *null* (point at nothing) and can be *re-pointed* to another object.

| | Reference `T&` | Pointer `T*` |
|---|---|---|
| can be null | no | yes (`nullptr`) |
| can be re-seated | no | yes |
| syntax to use | like the object | `*p`, `p->member` |
| use when | always refers to something | "optional" object, or re-pointing, or C APIs |

## Pointer arithmetic

If `p` points into an array, `p + 1` points to the *next element* (not the next byte). `p[i]` is exactly
`*(p + i)`. Arithmetic is only valid *within* the same array (and one-past-the-end); going outside is UB.

## const and pointers: read right to left

```cpp
const int* a;        // pointer to const int: can't modify *a, can re-point a
int* const b = &x;   // const pointer to int: can modify *b, can't re-point b
const int* const c = &x;  // neither
```

Trick: read the declaration right-to-left. `int* const b` = "b is a const pointer to int".

```cpp title="examples/week03/lesson02.cpp"
--8<-- "examples/week03/lesson02.cpp"
```

**Output**:

```text
--8<-- "examples/week03/lesson02.out"
```

## The wrong way: dereferencing null or dangling pointers

```cpp
int* p = nullptr;
*p = 1;              // UB: often a crash (SIGSEGV), but not guaranteed

int* q;
{ int local = 5; q = &local; }
*q = 6;              // UB: local is dead, q dangles
```

The fix is mostly *design*: prefer references when null isn't meaningful, keep pointers non-owning
(owning pointers are smart pointers — Week 12), and don't let a pointer outlive what it points to.

!!! note "About `void*`"
    `void*` can hold any object address but has no type. C APIs (like `pthread_create` or JNI) use it for
    "user data". In C++ code, prefer templates or `std::function`, and when you must use `void*`,
    `static_cast` it back to the *exact* original type.

## Key takeaways

!!! success "Key takeaways"
    - A pointer stores an address; `*p` is the object, `&x` is the address of `x`.
    - Pointer arithmetic moves by whole elements and is only valid within one array (plus one-past-the-end).
    - Read pointer declarations right to left: `const int*` vs `int* const`.
    - Use references when there's always an object; raw pointers for optional, non-owning access.

## Quiz

**Q1.** If `int a[4]` starts at address 1000 and `sizeof(int)==4`, what address is `a + 3`?

??? question "Show answer"
    1012 — arithmetic is in units of elements.

**Q2.** Which of these can you do with `const char* s`: `s = other;` / `*s = 'x';`?

??? question "Show answer"
    `s = other;` is fine (re-pointing). `*s = 'x';` is an error (the pointee is const).

**Q3.** When would you choose a pointer parameter over a reference?

??? question "Show answer"
    When "no object" is a legitimate input (null), or for C interop. Otherwise a reference documents that an object is required.

**Q4.** Is forming the pointer `a + 4` for `int a[4]` UB? Dereferencing it?

??? question "Show answer"
    Forming one-past-the-end is allowed (used as an end marker); dereferencing it is UB.

