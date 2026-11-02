# Lesson 9.3: std::optional and std::variant

<span class="stdtag">C++23</span> · about 11 minutes

## Why this matters

"Find the track with this ID" — the track might not exist. That's not an error worth an exception; it's a
normal outcome. Returning `-1` or `nullptr` as a magic value is how bugs are born. `std::optional` says
"maybe a value" in the type. And when the answer can be one of *several* types — a JSON value that's a
number, a string or a list — `std::variant` gives you a type-safe union.

## `std::optional<T>`

```cpp
std::optional<Track> find(int id);
if (auto t = find(42)) use(*t);         // contextually converts to bool
find(42).value_or(default_track);
```

`*opt` on an empty optional is UB; `opt.value()` throws `std::bad_optional_access`. C++23 adds monadic
operations so you can chain steps without nested `if`s:

```cpp
parse_int(s).transform([](int x) { return x * 2; })   // map the value if present
            .and_then(validate)                      // next step that also returns optional
            .value_or(0);
```

## `std::variant<Ts...>`

A variant holds exactly one of its alternatives, knows which, and won't let you read the wrong one. Read it
with `std::visit` and a visitor that handles *every* alternative — the compiler checks exhaustiveness.
The **overload pattern** builds a visitor from lambdas:

```cpp
template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };
```

```cpp title="examples/week09/lesson03.cpp"
--8<-- "examples/week09/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week09/lesson03.out"
```

## variant vs. inheritance

Both model "one of several kinds". Variant: closed set of types, value semantics, no heap allocation,
adding an *operation* is easy (write a new visitor). Inheritance: open set of types, adding a *type* is easy.
This trade-off is called the *expression problem*.

!!! warning "Pitfall"
    `std::variant<bool, std::string> v = "text";` — before C++20's fix (P0608) this chose `bool`! Modern
    compilers choose `std::string`, but be explicit with string literals in variants.

## Key takeaways

!!! success "Key takeaways"
    - `std::optional` encodes 'maybe a value' in the type; avoid magic sentinel values.
    - C++23 `and_then`/`transform`/`or_else` chain optional steps.
    - `std::variant` is a type-safe union; `std::visit` with the overload pattern handles every alternative.
    - Variant suits closed sets of types; inheritance suits open sets.

## Quiz

**Q1.** What happens on `*opt` when `opt` is empty?

??? question "Show answer"
    Undefined behaviour. Use `value()` (throws) or check first.

**Q2.** What's the difference between `and_then` and `transform` on optional?

??? question "Show answer"
    `transform` maps the value with a function returning a plain value; `and_then` takes a function that itself returns an optional, flattening the result.

**Q3.** Why use `std::monostate` as the first alternative?

??? question "Show answer"
    To give the variant a cheap default/'empty' state, e.g. when the other alternatives aren't default constructible or to represent null.

