WEEK = dict(num=9, title="Error handling and undefined behaviour", intro="""
Every real program fails: files are missing, packets are corrupt, memory runs out. This week compares C++'s
error-handling tools — exceptions, `std::optional`, `std::expected`, error codes, assertions — and gives
you a rule for choosing. We end with a catalogue of undefined behaviour, the class of bug that makes C++
uniquely dangerous, and the tools that catch it.
""", lessons=[
dict(title="Exceptions: throw, try, catch, and stack unwinding", std="C++20", minutes=11, area="Error handling",
features=[("`throw`, `try`, `catch`, rethrow `throw;`", "C++98"), ("Standard exception hierarchy (`<stdexcept>`)", "C++98"), ("Stack unwinding and RAII", "C++98"), ("`std::exception_ptr`, `std::current_exception`, `std::rethrow_exception`", "C++11"), ("`std::nested_exception`, `std::throw_with_nested`", "C++11"), ("Function-try-blocks", "C++98"), ("`-fno-exceptions` builds", "—")],
why="""
You're parsing a playlist file. Fifteen functions deep, you discover the file is corrupt. With error codes,
every one of those fifteen functions must check and pass the error up. Exceptions jump straight to the
code that can handle it — and RAII ensures everything in between is cleaned up on the way. That's the
idea; the details (what to throw, what to catch, what it costs) are this lesson.
""",
body="""
## The basics

```cpp
if (!file) throw std::runtime_error{"cannot open " + path};
...
try { load(path); }
catch (const std::runtime_error& e) { std::cerr << e.what(); }
```

- **Throw by value, catch by `const&`.** Catching by value slices and copies.
- Handlers are tried in order; put derived types before base types.
- `catch (...)` catches anything; `throw;` rethrows the current exception unchanged.

## Stack unwinding

When an exception propagates, every fully constructed local object on the way is destroyed — that's why
RAII (Week 4) makes exception-safe code natural. The example prints destructors as the stack unwinds.
If no handler is found, `std::terminate` is called (and whether the stack is unwound first is
implementation-defined).

{{ex}}

## The standard hierarchy

`std::exception` ← `std::logic_error` (bugs: `invalid_argument`, `out_of_range`, `length_error`) and
`std::runtime_error` (environment: `range_error`, `overflow_error`, `system_error`), plus `bad_alloc`,
`bad_cast`, `bad_variant_access`, `bad_optional_access`... Derive your own from `std::runtime_error` and
add context.

## Nesting and transporting

`std::throw_with_nested` wraps the current exception inside a new one with more context ("while loading
playlist X: cannot open file Y"). `std::exception_ptr` lets you carry an exception to another thread —
`std::future` uses it.

## Costs and no-exception builds

Mainstream implementations use "zero-cost" tables: **no** cost on the happy path, but a throw is slow
(microseconds) and binaries grow. So: exceptions for *exceptional* failures, not for control flow. Some
domains (games, embedded, parts of Android/Google code) compile with `-fno-exceptions`; then `throw` doesn't
compile and allocation failure terminates. Lesson 4 shows the alternatives.
""",
files={"": r'''
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>

struct Guard {
    std::string name;
    explicit Guard(std::string n) : name{std::move(n)} {}
    ~Guard() { std::cout << "  ~Guard(" << name << ")\n"; }
};

class ParseError : public std::runtime_error {
public:
    ParseError(const std::string& what, int line) : std::runtime_error{what}, line_{line} {}
    int line() const { return line_; }
private:
    int line_;
};

int parse_duration(const std::string& field, int line) {
    Guard g{"parse_duration"};
    std::size_t used = 0;
    int v = std::stoi(field, &used);                  // may throw std::invalid_argument
    if (used != field.size()) throw ParseError{"trailing junk in '" + field + "'", line};
    return v;
}

void load_playlist() {
    Guard g{"load_playlist"};
    try {
        parse_duration("12x", 7);
    } catch (...) {
        std::throw_with_nested(std::runtime_error{"while loading playlist.m3u"});
    }
}

void print_nested(const std::exception& e, int depth = 0) {
    std::cout << std::string(depth * 2, ' ') << "- " << e.what() << '\n';
    try { std::rethrow_if_nested(e); }
    catch (const std::exception& inner) { print_nested(inner, depth + 1); }
}

int main() {
    try {
        load_playlist();
    } catch (const std::exception& e) {
        std::cout << "caught:\n";
        print_nested(e);
    }

    try {
        parse_duration("abc", 3);
    } catch (const ParseError& e) {                   // most specific first
        std::cout << "ParseError at line " << e.line() << '\n';
    } catch (const std::invalid_argument& e) {
        std::cout << "invalid_argument from stoi\n";
    }

    std::exception_ptr saved;
    try { throw std::out_of_range{"index 9"}; } catch (...) { saved = std::current_exception(); }
    try { std::rethrow_exception(saved); }
    catch (const std::logic_error& e) { std::cout << "transported: " << e.what() << '\n'; }
}
'''},
takeaways=["Throw by value, catch by `const&`, most-derived handlers first.",
"Stack unwinding destroys locals, so RAII makes cleanup automatic.",
"Use `throw_with_nested` for context and `exception_ptr` to transport exceptions.",
"Exceptions are free when not thrown but slow when thrown; reserve them for genuinely exceptional failures."],
quiz=[("Why catch by `const&` rather than by value?", "Catching by value copies and slices derived exceptions to the caught type; a reference preserves the dynamic type and avoids the copy."),
("What happens if an exception is never caught?", "`std::terminate` is called."),
("What's the difference between `throw;` and `throw e;` in a handler?", "`throw;` rethrows the original exception object unchanged; `throw e;` throws a copy of `e`'s static type, possibly slicing.")]),

dict(title="Exception safety guarantees and noexcept", std="C++20", minutes=11, area="Error handling",
features=[("Exception safety guarantees (nothrow, strong, basic)", "—"), ("`noexcept` specifier and operator", "C++11"), ("Conditional `noexcept(expr)`", "C++11"), ("Destructors are implicitly `noexcept`", "C++11"), ("Copy-and-swap for the strong guarantee", "—"), ("`std::move_if_noexcept`", "C++11")],
why="""
Imagine a `Playlist::add` that throws halfway through: the track count was incremented but the track
wasn't stored. Now the object is lying. Exception *safety* is about what state your objects are in after
an exception. There are three standard levels of promise, and choosing deliberately is what makes C++ code
robust.
""",
body="""
## The three guarantees

| Guarantee | Promise | Example |
|---|---|---|
| **No-throw** | never throws | destructors, `swap`, move operations (ideally) |
| **Strong** | commit or rollback: on failure, state is unchanged | `std::vector::push_back` (with noexcept moves or copyable types) |
| **Basic** | no leaks, invariants hold, but state may have changed | most operations |

No guarantee at all = a bug.

## The wrong way

{{ex}}

`add_bad` updates the count first, then does the throwing work. `add_good` does all throwing work on the
side, then commits with operations that can't throw. That's the general recipe: **do the work, then
commit with no-throw operations**. Copy-and-swap (Week 5) is the same idea for assignment.

## `noexcept`

`noexcept` promises a function won't throw. If it throws anyway, `std::terminate` is called — no
unwinding guaranteed. Why bother?

1. Containers check it: `std::vector` *moves* during reallocation only if the move constructor is
   `noexcept` (or the type isn't copyable). You saw the copy counts in Week 5.
2. It documents intent and enables optimizations.

Destructors are `noexcept` by default; **never** let an exception escape one (throwing during unwinding
calls `std::terminate`).

Conditional form: `void swap(T& other) noexcept(std::is_nothrow_swappable_v<U>)`. The `noexcept(expr)`
*operator* asks whether an expression can throw.

!!! tip "Pro tip"
    Mark move constructors, move assignment, `swap`, and destructors `noexcept`. Don't sprinkle `noexcept`
    on everything else — if a function might ever need to throw, removing `noexcept` later is a breaking
    change.
""",
files={"": r'''
#include <iostream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

class Playlist {
public:
    void add_bad(const std::string& t) {
        ++count_;                                  // state changed...
        validate(t);                               // ...then a throw: count_ is now wrong
        tracks_.push_back(t);
    }
    void add_good(const std::string& t) {
        validate(t);                               // all throwing work first
        tracks_.push_back(t);                      // strong guarantee by itself
        ++count_;                                  // no-throw commit
    }
    void replace_all(std::vector<std::string> fresh) {   // strong: build aside, swap in
        for (const auto& t : fresh) validate(t);
        tracks_.swap(fresh);
        count_ = static_cast<int>(tracks_.size());
    }
    bool consistent() const { return count_ == static_cast<int>(tracks_.size()); }
private:
    static void validate(const std::string& t) { if (t.empty()) throw std::invalid_argument{"empty title"}; }
    std::vector<std::string> tracks_;
    int count_ = 0;
};

struct Thrower { Thrower() = default; Thrower(Thrower&&) {} };
struct Safe { Safe() = default; Safe(Safe&&) noexcept {} };

int main() {
    Playlist p;
    try { p.add_bad(""); } catch (const std::exception& e) { std::cout << "add_bad threw: " << e.what() << '\n'; }
    std::cout << "consistent after add_bad? " << std::boolalpha << p.consistent() << '\n';

    Playlist q;
    try { q.add_good(""); } catch (const std::exception&) {}
    std::cout << "consistent after add_good? " << q.consistent() << '\n';

    q.add_good("So What");
    try { q.replace_all({"A", "", "C"}); } catch (const std::exception&) {}
    std::cout << "consistent after failed replace_all? " << q.consistent() << '\n';

    std::cout << "noexcept(Thrower move)=" << std::is_nothrow_move_constructible_v<Thrower>
              << " noexcept(Safe move)=" << std::is_nothrow_move_constructible_v<Safe> << '\n';
    std::cout << "noexcept(p.consistent())=" << noexcept(p.consistent()) << '\n';
}
'''},
takeaways=["Know the three guarantees: no-throw, strong (commit/rollback), basic (valid but changed).",
"Recipe: do all throwing work first, then commit with no-throw operations.",
"`noexcept` moves let containers move instead of copy; violating `noexcept` calls `std::terminate`.",
"Never let exceptions escape destructors."],
quiz=[("What guarantee does `add_bad` provide?", "Not even the basic guarantee in a meaningful sense: the class invariant (count == size) is broken after the exception."),
("Why does `std::vector` care whether your move constructor is `noexcept`?", "To keep push_back's strong guarantee during reallocation: if a move could throw midway, the old buffer would be partially moved-from, so it copies instead."),
("What does `noexcept(p.consistent())` evaluate to here and why?", "`false`, because `consistent()` isn't declared `noexcept` — the operator checks declarations, not actual behaviour.")]),

dict(title="std::optional and std::variant", std="C++23", minutes=11, area="Error handling",
features=[("`std::optional`", "C++17"), ("Monadic `optional`: `and_then`, `transform`, `or_else`", "C++23"), ("`std::variant`, `std::visit`, `std::holds_alternative`, `std::get_if`", "C++17"), ("Overload pattern for visitors", "C++17"), ("`std::monostate`", "C++17"), ("`valueless_by_exception`", "C++17")],
why="""
"Find the track with this ID" — the track might not exist. That's not an error worth an exception; it's a
normal outcome. Returning `-1` or `nullptr` as a magic value is how bugs are born. `std::optional` says
"maybe a value" in the type. And when the answer can be one of *several* types — a JSON value that's a
number, a string or a list — `std::variant` gives you a type-safe union.
""",
body="""
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

{{ex}}

## variant vs. inheritance

Both model "one of several kinds". Variant: closed set of types, value semantics, no heap allocation,
adding an *operation* is easy (write a new visitor). Inheritance: open set of types, adding a *type* is easy.
This trade-off is called the *expression problem*.

!!! warning "Pitfall"
    `std::variant<bool, std::string> v = "text";` — before C++20's fix (P0608) this chose `bool`! Modern
    compilers choose `std::string`, but be explicit with string literals in variants.
""",
files={"": r'''
#include <charconv>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>
#include <variant>
#include <vector>

std::optional<int> parse_int(std::string_view s) {
    int v{};
    auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), v);
    if (ec != std::errc{} || p != s.data() + s.size()) return std::nullopt;
    return v;
}
std::optional<int> valid_bpm(int bpm) { return bpm >= 20 && bpm <= 300 ? std::optional{bpm} : std::nullopt; }

template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };

using Json = std::variant<std::monostate, double, std::string, std::vector<double>>;

std::string describe(const Json& j) {
    return std::visit(overloaded{
        [](std::monostate) { return std::string{"null"}; },
        [](double d) { return "number " + std::to_string(d); },
        [](const std::string& s) { return "string \"" + s + '"'; },
        [](const std::vector<double>& v) { return "array of " + std::to_string(v.size()); },
    }, j);
}

int main() {
    for (std::string_view s : {"120", "12x", "999"}) {
        auto bpm = parse_int(s).and_then(valid_bpm).transform([](int b) { return b * 2; });
        std::cout << s << " -> " << (bpm ? std::to_string(*bpm) + " half-beats/min" : std::string{"invalid"}) << '\n';
    }
    std::cout << "value_or: " << parse_int("oops").value_or(-1) << '\n';
    try { (void)parse_int("x").value(); } catch (const std::bad_optional_access&) { std::cout << "bad_optional_access\n"; }

    std::vector<Json> values{Json{}, 3.5, std::string{"hi"}, std::vector<double>{1, 2, 3}};
    for (const auto& j : values) std::cout << describe(j) << '\n';

    Json j = 2.0;
    std::cout << std::boolalpha << std::holds_alternative<double>(j) << ' ' << j.index() << '\n';
    if (auto* s = std::get_if<std::string>(&j)) std::cout << *s; else std::cout << "not a string\n";
    try { (void)std::get<std::string>(j); } catch (const std::bad_variant_access&) { std::cout << "bad_variant_access\n"; }
}
''', "std": "c++23"},
takeaways=["`std::optional` encodes 'maybe a value' in the type; avoid magic sentinel values.",
"C++23 `and_then`/`transform`/`or_else` chain optional steps.",
"`std::variant` is a type-safe union; `std::visit` with the overload pattern handles every alternative.",
"Variant suits closed sets of types; inheritance suits open sets."],
quiz=[("What happens on `*opt` when `opt` is empty?", "Undefined behaviour. Use `value()` (throws) or check first."),
("What's the difference between `and_then` and `transform` on optional?", "`transform` maps the value with a function returning a plain value; `and_then` takes a function that itself returns an optional, flattening the result."),
("Why use `std::monostate` as the first alternative?", "To give the variant a cheap default/'empty' state, e.g. when the other alternatives aren't default constructible or to represent null.")]),

dict(title="std::expected, error codes, and choosing a strategy", std="C++23", minutes=12, area="Error handling",
features=[("`std::expected<T, E>`, `std::unexpected`", "C++23"), ("Monadic `expected`: `and_then`, `transform`, `or_else`, `transform_error`", "C++23"), ("`std::error_code`, `std::error_condition`, `std::system_error`", "C++11"), ("`std::errc`", "C++11"), ("`[[nodiscard]]` on result types", "C++17"), ("Choosing exceptions vs. expected vs. optional vs. terminate", "—")],
why="""
`std::optional` tells you *that* something failed but not *why*. Exceptions tell you why, but they're
invisible in function signatures and unavailable in some builds. `std::expected<T, E>` (C++23) is the
middle path: a value *or* an error, explicit in the type, cheap, and works with `-fno-exceptions`. Let's
see it — and then settle the big question: which tool when?
""",
body="""
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

{{ex}}

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
""",
files={"": r'''
#include <cstdint>
#include <expected>
#include <filesystem>
#include <iostream>
#include <string>
#include <system_error>
#include <vector>

enum class ParseError { too_short, bad_magic, bad_channels };

std::string to_string(ParseError e) {
    switch (e) {
        case ParseError::too_short: return "too short";
        case ParseError::bad_magic: return "bad magic";
        case ParseError::bad_channels: return "bad channel count";
    }
    return "?";
}

struct Header { int channels; int rate; };

[[nodiscard]] std::expected<std::vector<std::uint8_t>, ParseError> check_size(std::vector<std::uint8_t> b) {
    if (b.size() < 6) return std::unexpected{ParseError::too_short};
    return b;
}
[[nodiscard]] std::expected<std::vector<std::uint8_t>, ParseError> check_magic(std::vector<std::uint8_t> b) {
    if (b[0] != 'S' || b[1] != 'N') return std::unexpected{ParseError::bad_magic};
    return b;
}
[[nodiscard]] std::expected<Header, ParseError> decode(const std::vector<std::uint8_t>& b) {
    if (b[2] == 0 || b[2] > 8) return std::unexpected{ParseError::bad_channels};
    return Header{b[2], (b[3] << 16) | (b[4] << 8) | b[5]};
}

void report(const std::vector<std::uint8_t>& bytes) {
    auto result = check_size(bytes).and_then(check_magic).and_then(decode)
                      .transform([](Header h) { return std::to_string(h.channels) + "ch @ " + std::to_string(h.rate) + " Hz"; })
                      .transform_error(to_string);
    std::cout << (result ? "ok: " + *result : "error: " + result.error()) << '\n';
}

int main() {
    report({'S', 'N', 2, 0x00, 0xBB, 0x80});
    report({'S', 'N', 2});
    report({'X', 'X', 2, 0, 0, 0});
    report({'S', 'N', 0, 0, 0, 0});

    std::error_code ec;
    auto size = std::filesystem::file_size("/definitely/not/here.wav", ec);   // non-throwing overload
    std::cout << "file_size failed? " << std::boolalpha << static_cast<bool>(ec)
              << " (no_such_file: " << (ec == std::errc::no_such_file_or_directory) << ")\n";
    (void)size;
    try {
        (void)std::filesystem::file_size("/definitely/not/here.wav");           // throwing overload
    } catch (const std::filesystem::filesystem_error& e) {
        std::cout << "filesystem_error code matches: " << (e.code() == std::errc::no_such_file_or_directory) << '\n';
    }
}
''', "std": "c++23"},
takeaways=["`std::expected<T, E>` makes failure explicit in the type and works without exceptions.",
"Chain fallible steps with `and_then`, map values with `transform`, map errors with `transform_error`.",
"`std::error_code` pairs a value with a category; many std APIs offer throwing and `error_code&` overloads.",
"Bugs → assert/terminate; expected outcomes → expected/optional; rare far-away failures → exceptions."],
quiz=[("How do you return an error from a function returning `std::expected<int, std::string>`?", "`return std::unexpected{std::string{\"message\"}};` (or `std::unexpected(\"message\")` where convertible)."),
("Why compare `ec == std::errc::no_such_file_or_directory` instead of `ec.value() == 2`?", "The comparison goes through error categories/conditions and is portable; raw values differ between platforms and categories."),
("Should a violated precondition (a caller bug) be reported with `std::expected`?", "Usually no — bugs should be caught by assertions/contracts and fixed, not returned as recoverable errors.")]),

dict(title="Assertions, contracts preview, and the undefined behaviour catalogue", std="C++23", minutes=14, area="Error handling",
features=[("`assert` and `NDEBUG`", "C++98"), ("`static_assert` (with and without message)", "C++11/17"), ("Contracts: `pre`, `post`, `contract_assert`", "C++26 (preview)"), ("Undefined behaviour catalogue", "—"), ("Unspecified vs implementation-defined vs undefined", "—"), ("Erroneous behaviour for uninitialized reads", "C++26 (preview)"), ("`std::unreachable`", "C++23")],
why="""
Undefined behaviour (UB) is the scariest phrase in C++. It doesn't mean "crashes"; it means *the standard
places no requirements* — the optimizer may assume it never happens, and your program can do anything,
including appear to work until the day it doesn't. This lesson is your field guide: what UB looks like,
how to catch it, and how assertions (and soon contracts) help you state your assumptions.
""",
body="""
## Three kinds of "it depends"

| Term | Meaning | Example |
|---|---|---|
| Implementation-defined | each implementation picks and documents | `sizeof(long)`, right shift of negative ints (pre-C++20) |
| Unspecified | one of several valid outcomes, not documented | order of evaluation of function arguments |
| **Undefined** | no requirements at all | signed overflow, out-of-bounds access |

## The UB catalogue

| UB | Example | Catch it with |
|---|---|---|
| Out-of-bounds access | `v[v.size()]` | ASan, `-D_GLIBCXX_ASSERTIONS`, `.at()` |
| Use after free / dangling | reference to a destroyed local, iterator after `push_back` | ASan |
| Double free / mismatched `new[]`/`delete` | | ASan |
| Signed integer overflow | `INT_MAX + 1` | UBSan, constexpr tests |
| Shift too far / negative shift | `1 << 32` | UBSan |
| Reading uninitialized variables | `int x; use(x);` | MSan, `-Wuninitialized`, C++26 makes it "erroneous" |
| Null pointer dereference | | UBSan, ASan |
| Strict aliasing violation | `*(float*)&some_int` | `-fstrict-aliasing` warnings; use `std::bit_cast` |
| Data race | two threads, one writes, no sync | TSan |
| Misaligned access | casting a `char*` buffer to `int*` | UBSan |
| Modifying a `const` object | `const_cast` then write | — |
| Infinite loop without side effects | `while(true){}` with no I/O/atomics | — |
| Returning without a value from non-void | | `-Wreturn-type` |
| Violating `std::unreachable()` | | debug builds |

## Why the optimizer makes it worse

{{ex}}

Because signed overflow is UB, the compiler may assume `x + 1 > x` is *always* true and delete your
overflow check. That's not a compiler bug; it's the contract you signed.

## Assertions

`assert(cond)` checks a condition in debug builds and is removed when `NDEBUG` is defined. Use it for
*internal invariants* — things that are true unless there's a bug. `static_assert` does the same at compile
time.

## Contracts (C++26 preview)

C++26 adds contract assertions as language syntax:

```cpp
int isqrt(int x)
    pre(x >= 0)
    post(r: r * r <= x);
// inside a body: contract_assert(cond);
```

The build chooses an *evaluation semantic* (ignore, observe, enforce, quick-enforce) and you can install a
violation handler. Compiler support is arriving in 2025–2026 (GCC trunk has an implementation); treat this
as a preview and keep using `assert` today.

!!! tip "Pro tip: the debug-build safety net"
    Add `-fsanitize=address,undefined -D_GLIBCXX_ASSERTIONS` (libstdc++) or `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_DEBUG`
    (libc++) to your test builds. Week 15 makes this a habit.
""",
files={"": r'''
#include <cassert>
#include <climits>
#include <iostream>
#include <utility>

// The overflow check the optimizer may delete: x + 1 can "never" be smaller than x
bool will_overflow_wrong(int x) { return x + 1 < x; }          // UB when x == INT_MAX
bool will_overflow_right(int x) { return x == INT_MAX; }       // check before doing the operation

constexpr int checked_add(int a, int b) {
    if ((b > 0 && a > INT_MAX - b) || (b < 0 && a < INT_MIN - b)) return 0;   // saturate-ish: no UB
    return a + b;
}
static_assert(checked_add(INT_MAX, 1) == 0);

enum class Mode { mono, stereo };
int channels(Mode m) {
    switch (m) {
        case Mode::mono: return 1;
        case Mode::stereo: return 2;
    }
    std::unreachable();                       // C++23: promise to the optimizer; UB if reached
}

int average(const int* v, int n) {
    assert(v != nullptr && n > 0 && "average: need at least one value");   // internal invariant
    long long s = 0;
    for (int i = 0; i < n; ++i) s += v[i];
    return static_cast<int>(s / n);
}

int main() {
    std::cout << std::boolalpha << "right check: " << will_overflow_right(INT_MAX) << '\n';
    std::cout << "checked_add(INT_MAX, 1) = " << checked_add(INT_MAX, 1) << '\n';
    std::cout << "channels(stereo) = " << channels(Mode::stereo) << '\n';
    int data[] = {3, 5, 10};
    std::cout << "average = " << average(data, 3) << '\n';
    (void)&will_overflow_wrong;               // shown, never called with INT_MAX
}
''', "_ubsan": {"expect": "san-detect", "san": ["undefined"], "flags": ["-fno-sanitize-recover=undefined"], "code": r'''
// Compiled with -fsanitize=undefined in CI: UBSan reports the signed overflow at run time.
#include <climits>
#include <cstdlib>
#include <iostream>
int main(int argc, char**) {
    int x = INT_MAX - 1 + argc;          // INT_MAX, but not a compile-time constant
    int y = x + 1;                       // signed overflow: UB
    std::cout << y << '\n';
    return EXIT_SUCCESS;
}
'''}},
takeaways=["UB means no requirements; optimizers assume it never happens and may delete your checks.",
"Check *before* an operation that could overflow; use `std::bit_cast` instead of type punning.",
"Use `assert` for internal invariants, `static_assert` for compile-time ones; contracts (C++26) are coming.",
"Run tests under ASan/UBSan/TSan and library hardening modes to catch UB early."],
quiz=[("Why can `x + 1 < x` be optimized to `false`?", "Signed overflow is UB, so the compiler may assume it doesn't happen; then `x + 1` is always greater than `x`."),
("Is the order of evaluation of function arguments undefined, unspecified or implementation-defined?", "Unspecified — the compiler can pick any order and need not document it; it's not UB by itself."),
("What happens to `assert` in a release build with `-DNDEBUG`?", "It expands to nothing; the condition isn't evaluated (so never put side effects in an assert).")]),
],
assignment=dict(std="c++23", title="A robust config parser", task="""
Parse lines of the form `key=value` into a `Config { int sample_rate; int channels; std::string device; }`.

- Return `std::expected<Config, ConfigError>` where `ConfigError` holds a line number and a message.
- Unknown keys, missing `=`, non-numeric numbers, out-of-range values and missing required keys are errors.
- Use `std::from_chars` (no exceptions in the parser).
- Print the result for one valid and three invalid inputs.
""", solution=r'''
#include <charconv>
#include <expected>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <string_view>

struct Config { int sample_rate = 0; int channels = 0; std::string device; };
struct ConfigError { int line; std::string message; };

std::expected<int, std::string> to_int(std::string_view s, int lo, int hi) {
    int v{};
    auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), v);
    if (ec != std::errc{} || p != s.data() + s.size()) return std::unexpected{"not a number: '" + std::string{s} + "'"};
    if (v < lo || v > hi) return std::unexpected{"out of range: " + std::string{s}};
    return v;
}

std::expected<Config, ConfigError> parse(const std::string& text) {
    Config c;
    std::istringstream in{text};
    std::string line;
    int n = 0;
    while (std::getline(in, line)) {
        ++n;
        if (line.empty() || line[0] == '#') continue;
        auto eq = line.find('=');
        if (eq == std::string::npos) return std::unexpected{ConfigError{n, "missing '='"}};
        std::string_view key{line.data(), eq}, value{line.data() + eq + 1, line.size() - eq - 1};
        if (key == "sample_rate") {
            auto v = to_int(value, 8000, 192000);
            if (!v) return std::unexpected{ConfigError{n, v.error()}};
            c.sample_rate = *v;
        } else if (key == "channels") {
            auto v = to_int(value, 1, 8);
            if (!v) return std::unexpected{ConfigError{n, v.error()}};
            c.channels = *v;
        } else if (key == "device") {
            c.device = value;
        } else {
            return std::unexpected{ConfigError{n, "unknown key '" + std::string{key} + "'"}};
        }
    }
    if (c.sample_rate == 0 || c.channels == 0) return std::unexpected{ConfigError{n, "sample_rate and channels are required"}};
    return c;
}

int main() {
    for (const char* text : {"# audio\nsample_rate=48000\nchannels=2\ndevice=hw:0\n",
                             "sample_rate=48k\nchannels=2\n",
                             "sample_rate=48000\nchanels=2\n",
                             "channels=2\n"}) {
        auto r = parse(text);
        if (r) std::cout << "ok: " << r->sample_rate << " Hz, " << r->channels << " ch, device '" << r->device << "'\n";
        else std::cout << "line " << r.error().line << ": " << r.error().message << '\n';
    }
}
'''))
