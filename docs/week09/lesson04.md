# Lesson 9.4: std::expected, error codes, and choosing a strategy

<span class="stdtag">C++23</span> · about 12 minutes

## Why this matters

`std::optional` tells you *that* something failed but not *why*. Exceptions tell you why, but they're
invisible in function signatures and unavailable in some builds. `std::expected<T, E>` (C++23) is the
middle path: a value *or* an error, explicit in the type, cheap, and works with `-fno-exceptions`. Let's
see it — and then settle the big question: which tool when?

## `std::expected`

```cpp
std::expected<Header, ParseError> parse_header(std::span<const std::byte>);

auto h = parse_header(bytes);
if (!h) report(h.error());
else use(*h);
```

Construct an error with `return std::unexpected{ParseError::truncated};`. Like optional, C++23 gives it
`and_then`, `transform`, `or_else` and `transform_error`, so a pipeline of fallible steps reads top to
bottom.

## `std::error_code`

The older standard mechanism, used by `<filesystem>`, `<system_error>` and networking-style APIs. An
`error_code` is an integer plus a *category* (generic, system, or your own), so codes from different
subsystems don't collide. Many std functions have two overloads: one that throws `std::system_error`, one
that takes `std::error_code&`.

```cpp title="examples/week09/lesson04.cpp"
--8<-- "examples/week09/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week09/lesson04.out"
```

## The decision

There's no single right answer, but here's a defensible default:

| Situation | Use |
|---|---|
| A bug (precondition violated, impossible state) | `assert` / contract / terminate — don't "handle" bugs |
| Rare failure, far from where it can be handled, exceptions enabled | exception |
| Failure is a normal, expected outcome, handled by the caller | `std::expected<T, E>` |
| "Not found" with no further information needed | `std::optional<T>` |
| Interop with OS / filesystem APIs | `std::error_code` |
| Constructors | exceptions (or a factory returning `expected`) |

Mark result-returning functions `[[nodiscard]]` so ignoring an error is a warning. (`std::expected` itself
is not marked nodiscard by every library, so put it on your functions.)

## Key takeaways

!!! success "Key takeaways"
    - `std::expected<T, E>` makes failure explicit in the type and works without exceptions.
    - Chain fallible steps with `and_then`, map values with `transform`, map errors with `transform_error`.
    - `std::error_code` pairs a value with a category; many std APIs offer throwing and `error_code&` overloads.
    - Bugs → assert/terminate; expected outcomes → expected/optional; rare far-away failures → exceptions.

## Quiz

**Q1.** How do you return an error from a function returning `std::expected<int, std::string>`?

??? question "Show answer"
    `return std::unexpected{std::string{"message"}};` (or `std::unexpected("message")` where convertible).

**Q2.** Why compare `ec == std::errc::no_such_file_or_directory` instead of `ec.value() == 2`?

??? question "Show answer"
    The comparison goes through error categories/conditions and is portable; raw values differ between platforms and categories.

**Q3.** Should a violated precondition (a caller bug) be reported with `std::expected`?

??? question "Show answer"
    Usually no — bugs should be caught by assertions/contracts and fixed, not returned as recoverable errors.

