# Lesson 16.5: C++26 preview: reflection, contracts, std::execution, and more

<span class="stdtag">C++26</span> · about 14 minutes

## Why this matters

C++26 is the biggest release since C++11. Static reflection alone will change how we write serialization,
bindings and logging. Compilers are implementing it now, so this lesson is honest about status: the C++26
code below is **not compiled by our checker** (marked preview); the runnable example shows the C++23 code
you write *today* for the same problems, so you can see what C++26 will replace.

## Static reflection (P2996)

```cpp
// C++26 (preview): print any aggregate's fields with no macros
template <typename T>
void print_fields(const T& obj) {
    template for (constexpr auto m : std::define_static_array(std::meta::nonstatic_data_members_of(^^T, std::meta::access_context::current())))
        std::println("{} = {}", std::meta::identifier_of(m), obj.[:m:]);
}
```

`^^T` reflects a type into a `std::meta::info` value; `[: m :]` splices it back into code. Serialization,
enum-to-string, ORM mappings and Python bindings become library code instead of macros or code generators.
(Experimental implementations: Bloomberg's clang-p2996 fork and EDG; GCC 16 has initial support.)

## Contracts (P2900)

```cpp
double rms(std::span<const float> xs)
    pre(!xs.empty())
    post(r: r >= 0.0);
```

Preconditions and postconditions become part of the declaration, checked according to a build-selected
evaluation semantic (ignore, observe, enforce, quick-enforce). `contract_assert(expr)` replaces `assert`.

## `std::execution` (P2300)

```cpp
auto work = stdexec::schedule(pool.get_scheduler())
          | stdexec::then([] { return decode(); })
          | stdexec::then([](Audio a) { return analyze(a); });
auto [report] = stdexec::sync_wait(std::move(work)).value();
```

Composable, cancellable async work with explicit schedulers — usable today via NVIDIA's `stdexec`.

## Smaller but welcome

- `std::inplace_vector<T, N>`: a vector with fixed capacity and no heap — perfect for embedded (Week 16.2).
- Pack indexing: `Ts...[0]` is the first type in a pack.
- `void f(int) = delete("use f(Channel)");` — deletion with a reason.
- `auto [_, value] = pair;` — `_` placeholders you can reuse.
- `#embed "logo.png"` — include binary data at compile time.
- `std::simd`, `std::hazard_pointer`, `std::rcu`, `std::linalg`, saturating arithmetic (`std::add_sat`).
- **Erroneous behaviour**: reading an uninitialized variable is no longer UB but "erroneous" (a defined,
  diagnosable value); hardened library preconditions are standardized.

## What you write today

```cpp title="examples/week16/lesson05.cpp"
--8<-- "examples/week16/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week16/lesson05.out"
```

Each block is the C++23 workaround for a C++26 feature: manual field lists (→ reflection), an assert macro
(→ contracts), `std::array` + size (→ `inplace_vector`), `std::tuple_element` (→ pack indexing),
`std::add_sat` emulation (→ saturating arithmetic).

## Key takeaways

!!! success "Key takeaways"
    - Static reflection (C++26) turns macros and code generators into ordinary library code.
    - Contracts make preconditions/postconditions part of declarations with selectable checking.
    - `std::execution` provides composable, cancellable async work; usable today via stdexec.
    - Many smaller features (inplace_vector, pack indexing, `_`, `#embed`, saturating math) remove workarounds.

## Quiz

**Q1.** What does `^^T` produce in C++26?

??? question "Show answer"
    A `std::meta::info` value representing the type `T` at compile time.

**Q2.** How do C++26 contracts differ from `assert`?

??? question "Show answer"
    They're part of the function declaration (visible to callers and tools) and have standardized evaluation semantics selectable at build time.

**Q3.** Which C++26 container replaces a hand-written fixed-capacity vector?

??? question "Show answer"
    `std::inplace_vector<T, N>`.

