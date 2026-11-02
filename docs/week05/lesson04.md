# Lesson 5.4: Copy elision, RVO, and returning by value

<span class="stdtag">C++20</span> · about 9 minutes

## Why this matters

Should a function that builds a big vector return it, or take an output parameter `void build(std::vector<int>& out)`?
Old advice said "output parameter, to avoid the copy". Modern C++ says: just return it. Let's see why the
compiler makes that free — and the two simple rules for writing parameters that take ownership.

## Guaranteed elision (C++17)

When you return a prvalue — `return Widget{args};` — C++17 *guarantees* the object is constructed
directly in the caller's storage. No copy, no move; the type doesn't even need to be copyable or movable.

## NRVO: named return value optimization

When you return a *named local*, `Widget w; ...; return w;`, the compiler is *allowed* (not required) to
construct `w` directly in the caller's storage. GCC and Clang do this whenever there's a single named
object returned on all paths. If it can't, **the return still moves** automatically (C++11, broadened in
C++20), never copies, as long as the type is movable.

```cpp title="examples/week05/lesson04.cpp"
--8<-- "examples/week05/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week05/lesson04.out"
```

Count the "move" lines: zero for the two common patterns. The function returning one of two different
locals can't use NRVO, so it moves.

## Sink parameters: take by value, then move

If a function will *store* its argument (a constructor storing a name, `push_back`-like functions), take it
**by value** and `std::move` it into place:

```cpp
class Track {
    std::string title_;
public:
    explicit Track(std::string title) : title_{std::move(title)} {}
};
Track a{some_string};          // one copy (into the parameter) + one cheap move
Track b{"literal"};            // constructs the parameter directly + one cheap move
Track c{std::move(s)};         // two cheap moves, no copy
```

One function handles lvalues and rvalues nearly optimally. (The alternative — overloading on `const&` and
`&&` — saves a move but doubles the code.)

!!! tip "Rules you can apply without thinking"
    1. Return by value. Don't `std::move` the return expression.
    2. Read-only parameter → `const T&` (or by value for cheap types / `string_view` / `span`).
    3. Parameter you'll store → by value + `std::move`.

## Key takeaways

!!! success "Key takeaways"
    - Returning a prvalue is guaranteed copy-free since C++17.
    - Returning a named local uses NRVO or, failing that, an implicit move — never write `return std::move(x)`.
    - Return results by value instead of using output parameters.
    - Sink parameters: take by value and `std::move` into the member.

## Quiz

**Q1.** Can a function return a non-copyable, non-movable type by value in C++17?

??? question "Show answer"
    Yes, if it returns a prvalue (`return T{...};`), thanks to guaranteed copy elision.

**Q2.** Why can't the compiler apply NRVO in `if (b) return x; return y;`?

??? question "Show answer"
    There are two different named objects that might be returned, so neither can be constructed in the caller's storage in advance. The return falls back to an implicit move.

**Q3.** What's the cost of `Track t{name};` with a by-value sink constructor, where `name` is an lvalue string?

??? question "Show answer"
    One copy (into the parameter) plus one move (into the member).

