# Lesson 8.4: Callables: std::function, move_only_function, and type erasure

<span class="stdtag">C++23</span> · about 11 minutes

## Why this matters

Lambdas each have a unique type. So how do you store *different* callbacks in one `std::vector`? Or keep a
callback as a class member without making the whole class a template? You need a type that can hold "any
callable with signature `void(int)`". That's `std::function` — and understanding how it works teaches you
**type erasure**, one of the most powerful designs in C++.

## The standard wrappers

| Wrapper | Owns? | Copyable? | Notes |
|---|---|---|---|
| `std::function<R(Args...)>` | yes | yes (requires copyable callable) | may heap-allocate; small-buffer optimization common |
| `std::move_only_function<R(Args...)>` (C++23) | yes | move-only | can hold lambdas capturing `unique_ptr`; const-correct |
| `std::function_ref<R(Args...)>` (C++26) | **no** | yes | cheap non-owning view for parameters |
| plain template parameter `F&&` | — | — | zero overhead, but makes your function a template |

Rule of thumb: function **parameters** that call immediately → template or (C++26) `function_ref`; stored
callbacks → `std::function` or `std::move_only_function`.

## `std::invoke`

Calls anything callable uniformly: functions, lambdas, *and* member function pointers
(`std::invoke(&Track::title, t)`). Generic code uses it so that users can pass member pointers too.

```cpp title="examples/week08/lesson04.cpp"
--8<-- "examples/week08/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week08/lesson04.out"
```

## How type erasure works

Inside, `std::function` holds a pointer to an abstract "concept" interface, and a templated "model" that
implements it for the concrete callable type. The template is only visible at construction; afterwards the
type is "erased" behind a virtual call. The example builds a tiny `AnyDrawable` the same way — runtime
polymorphism *without* requiring your types to inherit from anything.

!!! warning "Costs"
    Calling through `std::function` is an indirect call that's hard to inline, and storing a large lambda
    may allocate. Fine for event callbacks; avoid in per-sample DSP loops.

## Key takeaways

!!! success "Key takeaways"
    - `std::function` stores any copyable callable with a given signature; `std::move_only_function` (C++23) allows move-only ones.
    - `std::function_ref` (C++26) is a non-owning view for parameters.
    - `std::invoke` calls functions, lambdas and member pointers uniformly.
    - Type erasure = abstract concept + templated model, hidden behind a value-semantic wrapper.

## Quiz

**Q1.** Why can't `std::function` hold a lambda that captures a `std::unique_ptr`?

??? question "Show answer"
    `std::function` requires the callable to be copyable; such a lambda is move-only. Use `std::move_only_function`.

**Q2.** When should a function take a template `F&&` instead of `std::function`?

??? question "Show answer"
    When it calls the callable immediately and doesn't store it — the template has no type-erasure overhead and inlines.

**Q3.** In type erasure, where does the concrete type survive?

??? question "Show answer"
    Only inside the templated `Model<T>`, created in the wrapper's constructor template; the wrapper itself sees only the abstract `Concept`.

