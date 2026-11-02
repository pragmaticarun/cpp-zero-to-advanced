# Lesson 6.5: RTTI: typeid, dynamic_cast, and std::any

<span class="stdtag">C++20</span> · about 9 minutes

## Why this matters

Sometimes you hold an `Effect*` and need to know: "is this actually a `Reverb`?" C++ can answer at run time
with RTTI (run-time type information). It's useful, it's occasionally a design smell, and on embedded and
some Android builds it's turned off entirely. Let's see the tools and their trade-offs.

## `dynamic_cast`

`dynamic_cast<Derived*>(base_ptr)` returns a valid pointer if the object really is a `Derived` (or derived
from it), and `nullptr` otherwise. With references, failure throws `std::bad_cast`. It only works on
polymorphic types (at least one virtual function).

## `typeid`

`typeid(expr)` returns a `const std::type_info&` describing the *dynamic* type for polymorphic glvalues.
`type_info::name()` is implementation-defined (GCC/Clang return a mangled name like `6Reverb`), so use it
for debugging, not for logic. To use types as map keys, wrap them in `std::type_index`.

## `std::any` (C++17)

`std::any` holds a value of *any* copyable type and remembers which one; `std::any_cast<T>` gets it back
(throwing `std::bad_any_cast` on mismatch). It's handy for property bags and plugin metadata, but you lose
compile-time type checking — prefer `std::variant` (Week 9) when the set of types is known.

```cpp title="examples/week06/lesson05.cpp"
--8<-- "examples/week06/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week06/lesson05.out"
```

## The design smell

```cpp
if (auto* r = dynamic_cast<Reverb*>(e)) r->set_room(0.8f);
else if (auto* g = dynamic_cast<Gain*>(e)) g->set_gain(2.0f);
// ... a growing chain of casts
```

A chain of `dynamic_cast`s usually means a virtual function is missing (`e->apply_preset(p)`), or that
the set of types is closed and a `std::variant` + `std::visit` would be clearer and faster.

## No RTTI builds

Many embedded and game builds compile with `-fno-rtti` (and the Android NDK historically defaulted to it;
modern NDK CMake toolchains enable RTTI and exceptions by default). Without RTTI, `dynamic_cast` on
polymorphic types and `typeid` don't compile, and `std::any` is unavailable with some libraries. Design
libraries so the core doesn't require RTTI.

## Key takeaways

!!! success "Key takeaways"
    - `dynamic_cast` checks the dynamic type: null pointer or `std::bad_cast` on failure.
    - `typeid(...).name()` is implementation-defined; use `std::type_index` as a map key.
    - `std::any` stores any copyable value with runtime type checks; prefer `std::variant` for closed sets.
    - Chains of `dynamic_cast` are a design smell; some builds disable RTTI entirely.

## Quiz

**Q1.** What does `dynamic_cast<D*>(p)` return if `*p` isn't a `D`?

??? question "Show answer"
    `nullptr`. (The reference form throws `std::bad_cast`.)

**Q2.** Why shouldn't program logic depend on `typeid(x).name()`?

??? question "Show answer"
    Its contents are implementation-defined (and often mangled); they differ between compilers.

**Q3.** When is `std::variant` a better choice than `std::any`?

??? question "Show answer"
    When the set of possible types is known at compile time: variant is type-checked, needs no heap allocation, and supports exhaustive `std::visit`.

