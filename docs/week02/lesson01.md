# Lesson 2.1: Control flow: if, switch, loops, and range-for

<span class="stdtag">C++20</span> · about 9 minutes

## Why this matters

Imagine scanning a buffer of audio samples looking for the first one that clips. You need to loop, test
each value, and stop early. That's control flow, and C++ has a few modern touches — like declaring a
variable right inside an `if` — that make such code tighter and safer. Let's go through them quickly.

## `if` and the `if`-with-initializer

You've seen `if (cond) { ... } else { ... }`. Since C++17 you can put a declaration *inside* the `if`:

```cpp
if (auto it = settings.find("volume"); it != settings.end()) {
    use(it->second);
}   // `it` is out of scope here: it can't be misused later
```

The variable lives only as long as the `if`/`else`. Small scopes are a great habit: fewer names in play,
fewer chances to use a stale one.

## `switch`

`switch` works on integers and enums. Each `case` *falls through* to the next unless you `break`.
Accidental fallthrough is a classic bug, so compilers warn (`-Wimplicit-fallthrough`). When you
*mean* it, say so with `[[fallthrough]];`.

## Loops

```cpp
for (int i = 0; i < n; ++i) { ... }   // classic counted loop
while (cond) { ... }                  // test first
do { ... } while (cond);              // run at least once
for (const auto& x : container) { ... }   // range-based for (C++11)
```

Range-based `for` is the default for "do something with each element". Use `const auto&` to avoid
copying each element; use `auto&` if you want to modify them.

C++20 added an initializer to range-for too: `for (auto v = make(); auto x : v)`.

Here's everything together, finding the first clipped sample:

```cpp title="examples/week02/lesson01.cpp"
--8<-- "examples/week02/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week02/lesson01.out"
```

## A common mistake: modifying a copy

```cpp
for (auto s : samples) s *= 0.5f;   // WRONG: halves a copy; samples unchanged
for (auto& s : samples) s *= 0.5f;  // right
```

!!! tip "Pro tip"
    Before writing a loop, ask: "is there an algorithm for this?" Finding the first matching element is
    `std::ranges::find_if`. We'll do a full tour of algorithms in Week 11 — loops are still fine for now.

## Key takeaways

!!! success "Key takeaways"
    - Use `if (init; cond)` to keep helper variables scoped to the `if`.
    - `switch` cases fall through without `break`; mark intentional fallthrough with `[[fallthrough]]`.
    - Range-for with `const auto&` reads without copying; `auto&` modifies in place.

## Quiz

**Q1.** What's wrong with `for (auto x : v) x = 0;`?

??? question "Show answer"
    `x` is a copy of each element, so the vector is unchanged. Use `auto& x`.

**Q2.** Where is `it` visible in `if (auto it = m.find(k); it != m.end()) {...} else {...}`?

??? question "Show answer"
    In the condition, the `if` body *and* the `else` body, but not after the whole statement.

**Q3.** Why does the compiler warn about a `case` without `break`?

??? question "Show answer"
    Implicit fallthrough is a common bug. `[[fallthrough]];` documents that it's intentional and silences the warning.

