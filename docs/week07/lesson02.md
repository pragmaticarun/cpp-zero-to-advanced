# Lesson 7.2: Class templates, specialization, and CTAD

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

`std::vector<int>` and `std::vector<std::string>` are two different classes generated from one
template. In this lesson we'll write our own small class template — a fixed-size statistics window for
sensor readings — and learn how to customize it for particular types.

## A class template

```cpp
template <typename T, std::size_t N>
class Window { std::array<T, N> data_{}; ... };

Window<float, 4> w;     // a class generated for (float, 4)
```

Member functions are only instantiated if they're *used* — so a `Window<std::string, 3>` compiles fine as
long as you don't call `mean()` on it.

## Specialization

- **Full specialization** gives a completely different implementation for one exact set of arguments:
  `template <> struct TypeName<int> { ... };`
- **Partial specialization** (classes only, not functions) customizes for a *pattern*:
  `template <typename T> struct TypeName<T*> { ... };`

The standard library uses this everywhere (e.g. `std::hash<T>` specializations, `std::vector<bool>`, which
is a famous cautionary tale: it packs bits and so its `operator[]` doesn't return a real `bool&`).

## CTAD (C++17)

```cpp
std::pair p{1, 2.5};       // pair<int, double> — no need to spell out the arguments
std::vector v{1, 2, 3};    // vector<int>
```

The compiler deduces class template arguments from constructor arguments. When that doesn't work the way
you want, a **deduction guide** tells it how.

```cpp title="examples/week07/lesson02.cpp"
--8<-- "examples/week07/lesson02.cpp"
```

**Output**:

```text
--8<-- "examples/week07/lesson02.out"
```

## Alias and variable templates

```cpp
template <typename T> using Buffer = std::vector<T, MyAllocator<T>>;
template <typename T> constexpr T pi = T(3.14159265358979323846L);
```

!!! warning "Pitfall: CTAD with braces and copies"
    `std::vector v{std::vector{1,2}};` is `vector<int>` (copy), not `vector<vector<int>>`. CTAD prefers the
    copy deduction candidate. When in doubt, spell out the type.

## Key takeaways

!!! success "Key takeaways"
    - Class templates generate a class per argument set; unused members aren't instantiated.
    - Full specialization replaces the template for exact arguments; partial specialization matches patterns (classes only).
    - CTAD deduces class template arguments from constructors; deduction guides steer it.
    - Alias templates and variable templates shorten generic code.

## Quiz

**Q1.** Why does `Window<std::string, 2>` compile even though `mean()` divides by `static_cast<std::string>(size())`?

??? question "Show answer"
    Member functions of class templates are only instantiated when used; `mean()` is never called.

**Q2.** Can you partially specialize a function template?

??? question "Show answer"
    No. Only class (and variable) templates can be partially specialized; for functions use overloading or `if constexpr`.

**Q3.** What type does `std::pair p{1, 2.5};` have?

??? question "Show answer"
    `std::pair<int, double>`, via CTAD.

