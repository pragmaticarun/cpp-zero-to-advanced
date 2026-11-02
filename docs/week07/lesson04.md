# Lesson 7.4: Forwarding references and perfect forwarding

<span class="stdtag">C++20</span> · about 10 minutes

## Why this matters

Write a function `make_logged<T>(args...)` that constructs a `T` and logs it. If you take the arguments by
`const&`, you force copies of temporaries — moving becomes impossible. If you take them by `&&`, you can't
pass lvalues. You want to pass every argument *exactly as it came in*. That's perfect forwarding.

## `T&&` in a template is special

In a deduced context, `T&&` is a **forwarding reference**: it binds to anything.

- Pass an lvalue `std::string s` → `T = std::string&`, and `T&&` collapses to `std::string&`.
- Pass an rvalue → `T = std::string`, parameter type `std::string&&`.

**Reference collapsing** rule: `& &`, `& &&`, `&& &` → `&`; only `&& &&` → `&&`.

Note: `std::vector<T>&&` or a `T&&` in a *non-template* is just an rvalue reference, not a forwarding one.

## `std::forward`

Inside the function, a named parameter is always an lvalue. `std::forward<T>(arg)` casts it back to an
rvalue *only if* it was originally an rvalue. That's how `emplace_back` and `make_unique` pass your
arguments to the constructor without extra copies.

```cpp title="examples/week07/lesson04.cpp"
--8<-- "examples/week07/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week07/lesson04.out"
```

## The wrong way

```cpp
template <typename T> void wrapper(T&& x) { target(x); }             // always passes an lvalue: copies
template <typename T> void wrapper(T&& x) { target(std::move(x)); }  // moves from caller's lvalue: theft!
template <typename T> void wrapper(T&& x) { target(std::forward<T>(x)); }   // right
```

## `decltype(auto)`

If a wrapper *returns* what it calls, `auto` would decay references; `decltype(auto)` preserves the exact
return type, references included.

!!! warning "Pitfall"
    Forwarding-reference overloads are greedy: `template <class T> void f(T&&)` beats `void f(const
    std::string&)` for a non-const `std::string` lvalue. Avoid overloading on forwarding references, or
    constrain them with concepts (next week).

## Key takeaways

!!! success "Key takeaways"
    - `T&&` with deduced `T` is a forwarding reference; it binds to lvalues and rvalues.
    - Reference collapsing: any `&` wins; only `&& &&` stays `&&`.
    - `std::forward<T>(x)` preserves the original value category; use it exactly once per argument.
    - `decltype(auto)` preserves references in return types.

## Quiz

**Q1.** Is `void f(std::vector<T>&& v)` a forwarding reference?

??? question "Show answer"
    No — only plain `T&&` with `T` deduced is a forwarding reference; `std::vector<T>&&` is an rvalue reference.

**Q2.** What is `T` when you call `template<class T> void f(T&&)` with an lvalue `int x`?

??? question "Show answer"
    `T = int&`, so the parameter type collapses to `int&`.

**Q3.** Why is `std::move(x)` wrong inside a forwarding function?

??? question "Show answer"
    It would move from the caller's lvalues too, leaving their objects in a moved-from state unexpectedly.

