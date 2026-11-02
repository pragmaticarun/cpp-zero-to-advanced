# Lesson 11.3: Ranges and views

<span class="stdtag">C++23</span> · about 13 minutes

## Why this matters

"Take the clipped takes, get their names, uppercase them, first three." With classic algorithms that's three
temporary vectors and a loop. With C++20 ranges it's one readable pipeline that runs lazily — no
temporaries, nothing computed until you iterate. This is the biggest change to everyday C++ style since
lambdas.

## Views and pipes

A *view* is a lightweight, lazy range adaptor. Compose them with `|`:

```cpp
auto names = takes | std::views::filter(&Take::clipped)
                   | std::views::transform(&Take::name)
                   | std::views::take(3);
for (const auto& n : names) ...      // work happens here, element by element
```

C++23 adds `std::ranges::to<std::vector>()` to materialize a pipeline, plus many views: `zip`,
`enumerate`, `chunk`, `slide`, `stride`, `adjacent`, `cartesian_product`, `join_with`.

```cpp title="examples/week11/lesson03.cpp"
--8<-- "examples/week11/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week11/lesson03.out"
```

## Laziness has consequences

1. **Views don't own** (except `owning_view`). A view over a temporary vector dangles; the library catches
   some cases by returning `std::ranges::dangling` from algorithms called on temporaries.
2. **Some views cache.** `filter_view::begin()` caches its result, so iterating a filter view while
   modifying the underlying elements that affect the predicate is a bug, and a `const` filter view isn't
   iterable.
3. **Re-iterating recomputes.** A `transform` over an expensive function runs it again each pass;
   materialize with `ranges::to` if you iterate many times.

## Generators of values

`std::views::iota(1, 11)` counts; `std::views::iota(1)` is infinite — combine with `take`. `std::views::istream<int>(in)`
reads from a stream lazily.

!!! tip "Pro tip: debugging"
    If a pipeline won't compile, build it up one adaptor at a time. Ranges errors are long, but the first
    "constraints not satisfied" line usually names the culprit view.

## Key takeaways

!!! success "Key takeaways"
    - Views are lazy, composable with `|`, and don't own their data.
    - C++23 adds `ranges::to`, `zip`, `enumerate`, `chunk`, `slide` and more.
    - Mind laziness: dangling views, caching in `filter`, recomputation on re-iteration.
    - Range algorithms on temporaries return `std::ranges::dangling` to prevent use-after-free.

## Quiz

**Q1.** When does the work in `takes | views::filter(f) | views::transform(g)` happen?

??? question "Show answer"
    Lazily, element by element, as you iterate the resulting view — nothing is computed when the pipeline is built.

**Q2.** How do you turn a view into a `std::vector` in C++23?

??? question "Show answer"
    `view | std::ranges::to<std::vector>()`.

**Q3.** Why does `std::ranges::find(std::vector<int>{1,2,3}, 2)` return `std::ranges::dangling`?

??? question "Show answer"
    The argument is a temporary non-borrowed range; an iterator into it would dangle after the full expression, so the library returns a placeholder type that can't be dereferenced.

