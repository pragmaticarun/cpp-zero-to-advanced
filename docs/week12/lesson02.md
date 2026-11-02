# Lesson 12.2: shared_ptr, weak_ptr, and ownership graphs

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

Sometimes ownership really is shared: an audio buffer used by the player *and* the waveform view, and it
should live as long as either needs it. `std::shared_ptr` counts owners and frees the object when the last
one goes. It's convenient — and easy to overuse. Let's learn the cost, the cycle trap, and `weak_ptr`.

## How it works

A `shared_ptr` is two pointers: one to the object, one to a **control block** holding the strong count,
weak count and deleter. Copying increments the strong count *atomically* (thread-safe counting, not
thread-safe object access). `make_shared` allocates object and control block together: one allocation,
better locality.

## The cycle trap

```cpp
struct Node { std::shared_ptr<Node> next; std::shared_ptr<Node> prev; };   // a <-> b
```

If `a.next = b` and `b.prev = a`, neither count reaches zero — leak. Make the back-edge a
**`std::weak_ptr`**: it observes without owning. Call `lock()` to get a temporary `shared_ptr` (null if the
object is gone).

```cpp title="examples/week12/lesson02.cpp"
--8<-- "examples/week12/lesson02.cpp"
```

**Output**:

```text
--8<-- "examples/week12/lesson02.out"
```

## `enable_shared_from_this`

Inside a member function you sometimes need a `shared_ptr` to `this` (e.g. to register a callback that
keeps the object alive). Creating `std::shared_ptr<T>(this)` makes a *second* control block → double
delete. Inherit `std::enable_shared_from_this<T>` and call `shared_from_this()` instead.

## Guidelines

- Prefer `unique_ptr`; reach for `shared_ptr` only for genuinely shared lifetime. A `unique_ptr` converts to
  a `shared_ptr` later if needed.
- Don't pass `shared_ptr` by value "just in case" — each copy is an atomic increment and decrement.
- The aliasing constructor shares ownership of an object while pointing to one of its members.

## Key takeaways

!!! success "Key takeaways"
    - `shared_ptr` = object pointer + control block with atomic counts; `make_shared` allocates once.
    - Cycles of `shared_ptr` leak; use `weak_ptr` for back-edges and `lock()` to access.
    - Use `enable_shared_from_this` instead of `shared_ptr<T>(this)`.
    - Prefer `unique_ptr`; don't pass `shared_ptr` by value unless you're sharing ownership.

## Quiz

**Q1.** Is `shared_ptr` thread-safe?

??? question "Show answer"
    The reference counting is (atomic); accessing the pointed-to object or assigning to the same shared_ptr instance from several threads is not (use `std::atomic<std::shared_ptr<T>>` for the latter).

**Q2.** How does `weak_ptr` break a cycle?

??? question "Show answer"
    It doesn't contribute to the strong count, so the objects can be destroyed when external owners go away.

**Q3.** What goes wrong with `return std::shared_ptr<Session>(this);`?

??? question "Show answer"
    It creates a second, independent control block; both will delete the object — double free.

