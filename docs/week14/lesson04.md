# Lesson 14.4: Parallel algorithms and a preview of std::execution

<span class="stdtag">C++20</span> · about 10 minutes

## Why this matters

Often you don't need threads at all: you need "sort this faster" or "sum this faster". C++17 lets you add a
single argument — an execution policy — to most algorithms and let the library parallelize. It's the
cheapest speedup in the language, when it works.

## Execution policies

```cpp
std::sort(std::execution::par, v.begin(), v.end());
double total = std::reduce(std::execution::par_unseq, xs.begin(), xs.end(), 0.0);
```

| Policy | Meaning |
|---|---|
| `seq` | sequential |
| `par` | may run on multiple threads |
| `par_unseq` | multiple threads *and* vectorized — no locks or allocation inside your function! |
| `unseq` (C++20) | vectorized on one thread |

Your element functions must not race. `std::reduce` (unlike `accumulate`) may reorder operations, so the
operation must be associative and commutative — floating-point sums may differ slightly between runs.

```cpp title="examples/week14/lesson04.cpp"
--8<-- "examples/week14/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week14/lesson04.out"
```

!!! note "Library support"
    GCC's libstdc++ implements the parallel policies on top of Intel TBB (link `-ltbb`; without TBB they may
    run sequentially). MSVC supports them natively. libc++'s support is still experimental, which is why this
    example is marked "may be unsupported" locally.

## Preview: `std::execution` (C++26)

C++26 adds **senders/receivers** (P2300): a composable model for async work — `schedule(sched) |
then(f) | let_value(g)`, `when_all`, structured cancellation. It fixes `std::future`'s lack of
composition. Compilers are only starting to ship it (NVIDIA's `stdexec` is the reference implementation),
so we don't compile it here; see the C++26 preview lesson in Week 16.

## Key takeaways

!!! success "Key takeaways"
    - Adding an execution policy is the cheapest way to parallelize standard algorithms.
    - Element functions must be race-free; `par_unseq` forbids locks and allocation.
    - `std::reduce` may reorder operations — use associative, commutative ops.
    - `std::execution` (C++26) brings composable senders/receivers.

## Quiz

**Q1.** Why might `std::reduce` give a slightly different floating-point sum than `std::accumulate`?

??? question "Show answer"
    It may group and reorder additions, and FP addition isn't associative.

**Q2.** Can you lock a mutex inside a `par_unseq` lambda?

??? question "Show answer"
    No — vectorized execution may interleave iterations on one thread, so locking can deadlock; it's disallowed.

**Q3.** What does libstdc++ need for real parallel execution?

??? question "Show answer"
    Intel TBB (link with `-ltbb`).

