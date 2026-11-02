# Lesson 11.5: Generators and lazy sequences with std::generator (C++23)

<span class="stdtag">C++23</span> · about 9 minutes

## Why this matters

Some sequences are easiest to describe as a loop that *produces* values one at a time: walk a directory tree,
read packets until EOF, generate an infinite stream of test tones. `std::generator` lets you write that loop
with `co_yield` and hand it out as a range that callers can pipe through views. It's a preview of
coroutines, which Week 14 explains properly.

## Writing a generator

```cpp
std::generator<int> fibonacci() {
    int a = 0, b = 1;
    while (true) { co_yield a; a = std::exchange(b, a + b); }
}
for (int x : fibonacci() | std::views::take(10)) ...
```

The function body runs only as far as needed: each `co_yield` suspends it until the caller asks for the next
value. Infinite sequences are fine as long as the consumer stops.

```cpp title="examples/week11/lesson05.cpp"
--8<-- "examples/week11/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week11/lesson05.out"
```

## Recursive generators

`co_yield std::ranges::elements_of(child_generator());` yields everything from a nested generator — handy for
tree traversals.

## Support status (honest)

`std::generator` is C++23 and is implemented in GCC 14's libstdc++, and in MSVC. libc++ (used by Clang on
macOS and by our local test compiler) did not ship it at the time of writing, so this example is marked
"may be unsupported": our CI compiles and runs it with GCC. If your toolchain lacks it, Week 14 shows how to
write a minimal generator yourself.

!!! warning "Lifetime pitfall"
    A generator that takes parameters *by reference* keeps referring to them while suspended. Passing a
    temporary (`gen(std::string{"x"})`) leaves a dangling reference after the first suspension. Take
    coroutine parameters by value.

## Key takeaways

!!! success "Key takeaways"
    - `std::generator<T>` turns a `co_yield` loop into a lazy input range.
    - Generators compose with views; infinite generators are fine if the consumer stops.
    - `std::ranges::elements_of` yields from nested generators (recursion).
    - Take generator parameters by value; library support is still uneven (GCC 14+, MSVC).

## Quiz

**Q1.** What happens at `co_yield a;`?

??? question "Show answer"
    The generator produces `a` to the consumer and suspends; it resumes from that point when the consumer asks for the next value.

**Q2.** Why is `std::generator<int> g(const std::string& s)` risky?

??? question "Show answer"
    The coroutine may outlive the referenced argument (e.g. a temporary), leaving a dangling reference when resumed.

**Q3.** Is a generator a forward range?

??? question "Show answer"
    No — it's an input range: single-pass; you can iterate it only once.

