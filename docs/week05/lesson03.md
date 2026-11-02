# Lesson 5.3: Move semantics, std::move, and the Rules of Five and Zero

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

Returning a 4K video frame from a function, or pushing a big buffer into a `std::vector`, would copy
megabytes in C++98. With move semantics, it copies three pointers. That's not a micro-optimization — it
changes how you design APIs: you can pass and return big objects *by value* again, which is simpler and
safer. Let's write a move constructor and watch the difference.

## The idea: steal, then leave the source in a valid state

A **move constructor** `T(T&& other) noexcept` takes the resources out of `other` (pointers, handles) and
leaves `other` *valid but unspecified* — typically empty. Destroying or reassigning a moved-from object
must still work.

```cpp title="examples/week05/lesson03.cpp"
--8<-- "examples/week05/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week05/lesson03.out"
```

Look at the counts: the moves cost nothing like the copy.

## `std::move` doesn't move anything

`std::move(x)` is just a cast to `T&&` — it says "I'm done with `x`, you may steal from it". The actual
moving happens in the move constructor/assignment that then gets selected. Two consequences:

- `std::move` on a `const` object silently **copies** (a `const T&&` can't bind to `T&&`, so overload
  resolution falls back to the copy constructor).
- After `std::move(x)`, don't use `x` except to assign to it or destroy it.

## Why `noexcept` matters

When `std::vector` grows, it moves elements to the new storage — **only if the move constructor is
`noexcept`**. Otherwise it copies, so that if a copy throws it can leave the old storage intact (the strong
guarantee). Forget `noexcept` on your move constructor and vector growth silently becomes copies. The
example shows both.

## Rule of Five and Rule of Zero

- **Rule of Five**: if you write any of destructor / copy ctor / copy assign / move ctor / move assign,
  think about all five. (Declaring a destructor or copy operation suppresses the implicit moves!)
- **Rule of Zero**: better — design classes so they need *none*. Hold resources in members that manage
  themselves (`std::vector`, `std::string`, `std::unique_ptr`). Then the compiler-generated operations are
  correct and as efficient as possible.

```cpp
struct Track {                     // Rule of Zero: no special members written
    std::string title;
    std::vector<float> samples;
    std::unique_ptr<Decoder> dec;  // makes Track move-only, automatically
};
```

!!! warning "Common pitfall: `return std::move(local);`"
    Don't. It *prevents* copy elision (next lesson), and `return local;` already moves automatically.
    Compilers warn with `-Wpessimizing-move`.

## Key takeaways

!!! success "Key takeaways"
    - A move constructor steals resources and leaves the source valid but unspecified (usually empty).
    - `std::move` is only a cast; moving a `const` object copies.
    - Mark move operations `noexcept`, or `std::vector` will copy on reallocation.
    - Prefer the Rule of Zero; otherwise follow the Rule of Five.
    - Don't write `return std::move(local);`.

## Quiz

**Q1.** What does `std::move` actually do?

??? question "Show answer"
    `static_cast<T&&>` — it converts its argument to an xvalue so move overloads can be selected. It performs no moving itself.

**Q2.** Why might `std::vector<T>` copy elements during `push_back` even though `T` has a move constructor?

??? question "Show answer"
    If the move constructor isn't `noexcept` (and T is copyable), vector uses copies to keep the strong exception guarantee on reallocation (`std::move_if_noexcept`).

**Q3.** Your class declares only a destructor. Does it get an implicit move constructor?

??? question "Show answer"
    No. A user-declared destructor suppresses the implicit move operations; moves fall back to (deprecated) implicit copies. Either `= default` the moves or follow the Rule of Zero.

**Q4.** Is it OK to call `v.size()` on a moved-from `std::vector`?

??? question "Show answer"
    Yes — it's in a valid but unspecified state, so calling functions without preconditions is fine (in practice it's empty). Calling `v[0]` would not be OK without checking.

