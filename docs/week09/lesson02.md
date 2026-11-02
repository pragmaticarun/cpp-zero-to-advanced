# Lesson 9.2: Exception safety guarantees and noexcept

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

Imagine a `Playlist::add` that throws halfway through: the track count was incremented but the track
wasn't stored. Now the object is lying. Exception *safety* is about what state your objects are in after
an exception. There are three standard levels of promise, and choosing deliberately is what makes C++ code
robust.

## The three guarantees

| Guarantee | Promise | Example |
|---|---|---|
| **No-throw** | never throws | destructors, `swap`, move operations (ideally) |
| **Strong** | commit or rollback: on failure, state is unchanged | `std::vector::push_back` (with noexcept moves or copyable types) |
| **Basic** | no leaks, invariants hold, but state may have changed | most operations |

No guarantee at all = a bug.

## The wrong way

```cpp title="examples/week09/lesson02.cpp"
--8<-- "examples/week09/lesson02.cpp"
```

**Output**:

```text
--8<-- "examples/week09/lesson02.out"
```

`add_bad` updates the count first, then does the throwing work. `add_good` does all throwing work on the
side, then commits with operations that can't throw. That's the general recipe: **do the work, then
commit with no-throw operations**. Copy-and-swap (Week 5) is the same idea for assignment.

## `noexcept`

`noexcept` promises a function won't throw. If it throws anyway, `std::terminate` is called — no
unwinding guaranteed. Why bother?

1. Containers check it: `std::vector` *moves* during reallocation only if the move constructor is
   `noexcept` (or the type isn't copyable). You saw the copy counts in Week 5.
2. It documents intent and enables optimizations.

Destructors are `noexcept` by default; **never** let an exception escape one (throwing during unwinding
calls `std::terminate`).

Conditional form: `void swap(T& other) noexcept(std::is_nothrow_swappable_v<U>)`. The `noexcept(expr)`
*operator* asks whether an expression can throw.

!!! tip "Pro tip"
    Mark move constructors, move assignment, `swap`, and destructors `noexcept`. Don't sprinkle `noexcept`
    on everything else — if a function might ever need to throw, removing `noexcept` later is a breaking
    change.

## Key takeaways

!!! success "Key takeaways"
    - Know the three guarantees: no-throw, strong (commit/rollback), basic (valid but changed).
    - Recipe: do all throwing work first, then commit with no-throw operations.
    - `noexcept` moves let containers move instead of copy; violating `noexcept` calls `std::terminate`.
    - Never let exceptions escape destructors.

## Quiz

**Q1.** What guarantee does `add_bad` provide?

??? question "Show answer"
    Not even the basic guarantee in a meaningful sense: the class invariant (count == size) is broken after the exception.

**Q2.** Why does `std::vector` care whether your move constructor is `noexcept`?

??? question "Show answer"
    To keep push_back's strong guarantee during reallocation: if a move could throw midway, the old buffer would be partially moved-from, so it copies instead.

**Q3.** What does `noexcept(p.consistent())` evaluate to here and why?

??? question "Show answer"
    `false`, because `consistent()` isn't declared `noexcept` — the operator checks declarations, not actual behaviour.

