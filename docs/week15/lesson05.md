# Lesson 15.5: Performance: caches, memory layout, and data-oriented design

<span class="stdtag">C++20</span> · about 13 minutes

## Why this matters

A main-memory access costs ~100 ns; an L1 cache hit ~1 ns. On modern hardware, *how your data is laid out*
often matters more than the algorithm's big-O constant. Data-oriented design — organizing data for the way
it's accessed — routinely gives 2–10× speedups in games, audio and simulation code.

## The rules of thumb

1. **Contiguous beats linked**: `std::vector` iterates at memory bandwidth; `std::list` chases pointers and
   misses cache on every node.
2. **Only load what you use**: if a loop touches one field of a 64-byte struct, you load 64 bytes to use 4.
3. **Avoid allocations in hot loops**: `reserve`, reuse buffers, use arenas (Week 12).
4. **Predictable branches are cheap; unpredictable ones cost ~15 cycles** each.

## AoS vs SoA

```cpp
struct Particle { float x, y, z, vx, vy, vz; std::uint32_t color; bool alive; };   // AoS
struct Particles { std::vector<float> x, y, z, vx, vy, vz; ... };                  // SoA
```

Updating positions in SoA streams through tightly packed arrays (and vectorizes); AoS drags the unused
fields through the cache.

```cpp title="examples/week15/lesson05.cpp"
--8<-- "examples/week15/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week15/lesson05.out"
```

The example also shows **padding**: member order changes `sizeof`. Timings print to stderr since they're
machine-dependent; on typical hardware SoA and vector traversal are several times faster.

!!! tip "Pro tip"
    Don't restructure everything into SoA. Do it for the hot data that profiling identifies. Clear code first,
    then optimize with evidence.

## Key takeaways

!!! success "Key takeaways"
    - Memory access patterns often dominate performance; keep hot data contiguous.
    - SoA layouts stream only the fields a loop uses and vectorize well.
    - Order members largest-to-smallest to reduce padding.
    - Optimize the hot path identified by profiling, not everything.

## Quiz

**Q1.** Why is iterating a `std::list` slower than a `std::vector` of the same size?

??? question "Show answer"
    List nodes are scattered in memory, so each step is a likely cache miss; vector elements are contiguous and prefetched.

**Q2.** What is `sizeof(struct { char a; double b; char c; })` on a typical 64-bit ABI?

??? question "Show answer"
    24 bytes due to padding for 8-byte alignment of `double`.

**Q3.** When does SoA beat AoS?

??? question "Show answer"
    When hot loops access only a few fields of many objects.

