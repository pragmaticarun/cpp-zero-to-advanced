# Lesson 12.3: Allocators and polymorphic memory resources (pmr)

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

In a real-time audio callback you're not allowed to call `malloc` — it may take a lock and blow your 2 ms
deadline. In a game, you want all per-frame allocations to come from one arena that's reset each frame.
Allocators let you keep using `std::vector` and `std::string` while controlling *where* their memory comes
from. C++17's `pmr` makes this practical.

## Classic allocators — and why they were painful

Containers take an allocator template parameter: `std::vector<int, MyAlloc<int>>`. But the allocator is
part of the *type*, so a `vector<int, A>` can't be passed where `vector<int>` is expected. That limited
their use.

## `std::pmr` (C++17)

`std::pmr::polymorphic_allocator` holds a pointer to a `std::pmr::memory_resource` and forwards to it via
virtual calls. `std::pmr::vector<int>` is one type regardless of the resource. The standard resources:

| Resource | Behaviour |
|---|---|
| `monotonic_buffer_resource` | bump-pointer arena; `deallocate` is a no-op; free all at once. Very fast. |
| `unsynchronized_pool_resource` | pools of fixed-size blocks; single-threaded |
| `synchronized_pool_resource` | same, thread-safe |
| `new_delete_resource()` | the global heap |
| `null_memory_resource()` | throws on any allocation — great as an upstream to *prove* you never hit the heap |

```cpp title="examples/week12/lesson03.cpp"
--8<-- "examples/week12/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week12/lesson03.out"
```

The example builds a vector of strings inside a stack buffer and proves no heap allocation happens by
using `null_memory_resource()` as the fallback. Note that `pmr` containers propagate the allocator to
their elements (`pmr::string` inside `pmr::vector` uses the same arena).

## Replacing global `operator new`

You can replace `operator new`/`operator delete` globally to count or trace allocations — useful in tests
("this function must not allocate"). The example counts global allocations.

!!! warning "Pitfall"
    A monotonic arena never reuses memory until it's destroyed or `release()`d. Great for per-frame or
    per-request work; bad for long-lived containers that grow and shrink.

## Key takeaways

!!! success "Key takeaways"
    - Allocators control where container memory comes from; classic ones are part of the type.
    - `std::pmr` containers share one type and take a `memory_resource*` at run time.
    - `monotonic_buffer_resource` is a fast arena; `null_memory_resource` proves no heap fallback.
    - Replacing global `operator new` lets tests count or forbid allocations.

## Quiz

**Q1.** Why can't you pass `std::vector<int, MyAlloc<int>>` to a function taking `const std::vector<int>&`?

??? question "Show answer"
    The allocator is a template parameter, so they're different types.

**Q2.** What does `deallocate` do on a `monotonic_buffer_resource`?

??? question "Show answer"
    Nothing — memory is only reclaimed when the resource is released or destroyed.

**Q3.** Why use `null_memory_resource()` as an upstream?

??? question "Show answer"
    Any allocation that doesn't fit the buffer throws `bad_alloc` instead of silently using the heap, proving the code stays within the arena.

