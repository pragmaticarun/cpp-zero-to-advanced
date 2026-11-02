# Lesson 8.5: CRTP, deducing this, and a taste of metaprogramming

<span class="stdtag">C++23</span> · about 11 minutes

## Why this matters

Virtual functions cost an indirect call and block inlining. If you know all types at compile time, you can
get polymorphism with *zero* runtime cost: the base class template knows the derived type and calls it
directly. That's CRTP — and C++23's "deducing this" makes much of it simpler. This lesson is
intermediate-to-advanced; it's fine to skim the metaprogramming part on a first pass.

## CRTP

```cpp
template <typename Derived>
struct Shape {
    double area() const { return static_cast<const Derived&>(*this).area_impl(); }
};
struct Square : Shape<Square> { double area_impl() const; };
```

The base is parameterized by the derived class, so the call is resolved at compile time. Uses: mixins
(add `operator!=` from `operator==`, add counting, add `clone()`), and static interfaces in performance
code. Downsides: no common base type for a heterogeneous container, and more template code.

## Deducing `this` (C++23)

An *explicit object parameter* makes the object a normal, deducible parameter:

```cpp
struct Counter {
    template <typename Self>
    auto& get(this Self& self) { return self.value; }   // one function for const and non-const
};
```

This removes duplicated const/non-const overloads, enables recursive lambdas, and replaces many CRTP
mixins — `this auto& self` deduces the *derived* type even when the function is declared in a base.

```cpp title="examples/week08/lesson05.cpp"
--8<-- "examples/week08/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week08/lesson05.out"
```

## Metaprogramming in one breath

Templates are Turing complete; you can compute with types. Modern code mostly uses `constexpr` for values
and concepts for constraints, but `std::index_sequence` (compile-time list of indices) is still everyday
useful, e.g. for iterating over a tuple — see the example's `print_tuple`. **Expression templates** (used by
Eigen and similar libraries) build an expression tree as types so that `a + b + c` on vectors runs as one
loop with no temporaries — a topic for further reading.

## Key takeaways

!!! success "Key takeaways"
    - CRTP gives compile-time polymorphism and mixins with no virtual calls.
    - Deducing `this` (C++23) deduces the object's type: one function for const/non-const, recursive lambdas, simpler mixins.
    - Use `std::index_sequence` to expand over tuple elements at compile time.
    - Pick dynamic polymorphism for open, runtime sets of types; static for known types in hot paths.

## Quiz

**Q1.** What's the main limitation of CRTP vs virtual functions?

??? question "Show answer"
    No common base type: `Shape<Square>` and `Shape<Circle>` are unrelated, so you can't store them in one container and choose at run time.

**Q2.** What does `template <typename Self> auto& get(this Self& self)` replace?

??? question "Show answer"
    A pair of overloads `T& get()` and `const T& get() const` (and possibly && versions).

**Q3.** Why does `InstanceCounter<Widget>::count` differ from `InstanceCounter<Gadget>::count`?

??? question "Show answer"
    They're different class template instantiations, each with its own static member.

