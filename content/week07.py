WEEK = dict(num=7, title="Templates: generic programming", intro="""
Templates are how C++ writes code once and uses it for many types — without the runtime cost of virtual
calls. The whole standard library is built on them. This week goes from function templates to type traits;
next week adds concepts and compile-time programming on top.

Honest warning: templates have the worst error messages in the language. We'll show you how to read them,
and Week 8's concepts make them dramatically better.
""", lessons=[
dict(title="Function templates and argument deduction", std="C++20", minutes=11, area="Templates & generic programming",
features=[("Function templates", "C++98"), ("Template argument deduction", "C++98"), ("Explicit template arguments", "C++98"), ("Abbreviated function templates (`auto` parameters)", "C++20"), ("Two-phase lookup, `typename` disambiguator", "C++98"), ("Templates in headers (instantiation model)", "C++98")],
why="""
You've written `clamp` for `int`. Now you need it for `float`, `double`, and `std::chrono::milliseconds`.
Copy-pasting four versions is how bugs multiply. A function template is a recipe: the compiler stamps out a
real function for each type you use — and each one is as fast as if you'd written it by hand.
""",
body="""
## The recipe

```cpp
template <typename T>
T clamp_to(T v, T lo, T hi) { return v < lo ? lo : (hi < v ? hi : v); }

clamp_to(15, 0, 10);        // T deduced as int
clamp_to(0.7, 0.0, 1.0);    // T deduced as double
```

The compiler **deduces** `T` from the arguments, then **instantiates** `clamp_to<int>` — real machine code,
no runtime dispatch.

## The wrong way: conflicting deductions

```cpp
clamp_to(0.7, 0, 1);   // error: T deduced as double AND int
```

Deduction doesn't do conversions. Fix it by making the arguments agree (`0.0, 1.0`), or by specifying
`T` explicitly: `clamp_to<double>(0.7, 0, 1)`.

{{ex}}

## Abbreviated templates (C++20)

`auto` in a parameter list makes a function a template:

```cpp
void print_all(const auto& container);   // same as template <typename C> void print_all(const C&)
```

## Templates live in headers

A template isn't code until it's instantiated, and the compiler needs the *definition* to instantiate it.
So templates normally go entirely in headers. (Explicit instantiation and modules — Week 15 — are the
exceptions.)

## `typename` for dependent names

Inside a template, `T::value_type` could be a type or a static member; the compiler assumes *value* unless
you say `typename T::value_type`. Since C++20 many contexts no longer need it, but you'll see it everywhere.

!!! tip "Reading template errors"
    Scroll to the **first** error, then find the line in *your* code ("required from here"). The library
    internals in the middle are rarely the problem.
""",
files={"": r'''
#include <chrono>
#include <iostream>
#include <string>
#include <vector>

template <typename T>
T clamp_to(T v, T lo, T hi) { return v < lo ? lo : (hi < v ? hi : v); }

template <typename T>
typename T::value_type sum(const T& c) {          // `typename`: dependent type name
    typename T::value_type total{};
    for (const auto& x : c) total += x;
    return total;
}

void print_all(const auto& c) {                   // abbreviated function template (C++20)
    for (const auto& x : c) std::cout << x << ' ';
    std::cout << '\n';
}

int main() {
    using namespace std::chrono_literals;
    std::cout << clamp_to(15, 0, 10) << '\n';
    std::cout << clamp_to(0.7, 0.0, 1.0) << '\n';
    std::cout << clamp_to<double>(1.7, 0, 1) << '\n';           // explicit T
    std::cout << clamp_to(250ms, 0ms, 100ms).count() << "ms\n";  // works for any type with <
    std::cout << clamp_to(std::string{"m"}, std::string{"a"}, std::string{"k"}) << '\n';

    std::vector<int> v{1, 2, 3, 4};
    std::cout << sum(v) << '\n';
    print_all(v);
    print_all(std::vector<std::string>{"templates", "are", "recipes"});
}
''', "_bad": {"expect": "fail", "code": r'''
template <typename T>
T clamp_to(T v, T lo, T hi) { return v < lo ? lo : (hi < v ? hi : v); }
int main() { return static_cast<int>(clamp_to(0.7, 0, 1)); }   // error: conflicting T
'''}},
takeaways=["A function template is a recipe; each set of deduced types instantiates a real function.",
"Deduction requires arguments to agree; no implicit conversions during deduction.",
"`auto` parameters (C++20) create abbreviated templates.",
"Template definitions usually live in headers; read errors from the first one, looking for your code."],
quiz=[("Why does `clamp_to(0.7, 0, 1)` fail?", "`T` is deduced as `double` from the first argument and `int` from the others; deduction fails because they conflict."),
("Do templates have a runtime cost compared to hand-written overloads?", "No — instantiations are ordinary functions. The costs are compile time and code size."),
("Why are templates usually defined in headers?", "The compiler needs the full definition at the point of instantiation in each translation unit.")]),

dict(title="Class templates, specialization, and CTAD", std="C++20", minutes=12, area="Templates & generic programming",
features=[("Class templates", "C++98"), ("Member function templates", "C++98"), ("Full specialization", "C++98"), ("Partial specialization", "C++98"), ("Class template argument deduction (CTAD) and deduction guides", "C++17"), ("Alias templates (`using`)", "C++11"), ("Variable templates", "C++14")],
why="""
`std::vector<int>` and `std::vector<std::string>` are two different classes generated from one
template. In this lesson we'll write our own small class template — a fixed-size statistics window for
sensor readings — and learn how to customize it for particular types.
""",
body="""
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

{{ex}}

## Alias and variable templates

```cpp
template <typename T> using Buffer = std::vector<T, MyAllocator<T>>;
template <typename T> constexpr T pi = T(3.14159265358979323846L);
```

!!! warning "Pitfall: CTAD with braces and copies"
    `std::vector v{std::vector{1,2}};` is `vector<int>` (copy), not `vector<vector<int>>`. CTAD prefers the
    copy deduction candidate. When in doubt, spell out the type.
""",
files={"": r'''
#include <array>
#include <cstddef>
#include <iostream>
#include <string>
#include <vector>

template <typename T, std::size_t N>
class Window {                                    // fixed-size rolling window
public:
    void push(T v) { data_[next_ % N] = v; ++next_; }
    std::size_t size() const { return next_ < N ? next_ : N; }
    T mean() const {                              // only instantiated if used
        T total{};
        for (std::size_t i = 0; i < size(); ++i) total += data_[i];
        return total / static_cast<T>(size());
    }
private:
    std::array<T, N> data_{};
    std::size_t next_ = 0;
};

template <typename T> struct TypeName { static std::string get() { return "unknown"; } };
template <> struct TypeName<int> { static std::string get() { return "int"; } };          // full
template <> struct TypeName<float> { static std::string get() { return "float"; } };
template <typename T> struct TypeName<T*> {                                              // partial
    static std::string get() { return "pointer to " + TypeName<T>::get(); }
};

template <typename T>
struct Tagged {
    T value;
    std::string tag;
};
Tagged(const char*, const char*) -> Tagged<std::string>;   // deduction guide

template <typename T> constexpr T pi = T(3.14159265358979323846L);   // variable template
template <typename T> using Grid = std::vector<std::vector<T>>;      // alias template

int main() {
    Window<float, 4> w;
    for (float x : {1.0f, 2.0f, 3.0f, 4.0f, 10.0f}) w.push(x);
    std::cout << "mean of last 4: " << w.mean() << '\n';

    Window<std::string, 2> names;                 // fine: mean() never instantiated
    names.push("a");
    std::cout << "names.size()=" << names.size() << '\n';

    std::cout << TypeName<int>::get() << ", " << TypeName<float**>::get() << ", "
              << TypeName<double>::get() << '\n';

    std::pair p{1, 2.5};                          // CTAD: pair<int, double>
    Tagged t{"hello", "greeting"};                // guide: Tagged<std::string>
    std::cout << p.second << ' ' << t.value.size() << '\n';
    std::cout << pi<float> << ' ' << pi<double> << '\n';
    Grid<int> g(2, std::vector<int>(3, 7));
    std::cout << g.size() << 'x' << g[0].size() << '\n';
}
'''},
takeaways=["Class templates generate a class per argument set; unused members aren't instantiated.",
"Full specialization replaces the template for exact arguments; partial specialization matches patterns (classes only).",
"CTAD deduces class template arguments from constructors; deduction guides steer it.",
"Alias templates and variable templates shorten generic code."],
quiz=[("Why does `Window<std::string, 2>` compile even though `mean()` divides by `static_cast<std::string>(size())`?", "Member functions of class templates are only instantiated when used; `mean()` is never called."),
("Can you partially specialize a function template?", "No. Only class (and variable) templates can be partially specialized; for functions use overloading or `if constexpr`."),
("What type does `std::pair p{1, 2.5};` have?", "`std::pair<int, double>`, via CTAD.")]),

dict(title="Non-type parameters, variadic templates, and fold expressions", std="C++20", minutes=11, area="Templates & generic programming",
features=[("Non-type template parameters (NTTP)", "C++98"), ("`auto` NTTP", "C++17"), ("Class-type NTTPs (structural types)", "C++20"), ("Variadic templates, parameter packs, `sizeof...`", "C++11"), ("Fold expressions", "C++17"), ("Template template parameters", "C++98")],
why="""
How does `std::make_unique` accept *any* number of constructor arguments? How does `std::format` take any
number of values? The answer is **variadic templates** — templates that take packs of types. Combined with
fold expressions, they let you write "do this for every argument" in a single line.
""",
body="""
## Non-type template parameters

Template parameters can be values, not just types: `std::array<int, 8>` takes the size `8`.
Allowed: integers, enums, pointers, `auto` (C++17), and since C++20 floating-point and *structural* class
types (all public, non-mutable members) — so you can even pass a small string literal wrapper.

## Parameter packs

```cpp
template <typename... Args>          // a pack of types
void log(const Args&... args);       // a pack of function parameters
sizeof...(Args)                      // how many
```

## Fold expressions (C++17)

Fold over a binary operator:

| Fold | Expands to |
|---|---|
| `(args + ...)` | `a1 + (a2 + (a3))` |
| `(... + args)` | `((a1) + a2) + a3` |
| `(init + ... + args)` | with an initial value — safe for empty packs |
| `((std::cout << args), ...)` | comma fold: "do this for each" |

{{ex}}

## The old way: recursion

Before C++17 you'd write a base case and a recursive case peeling off one argument at a time. You'll see
it in older code; folds and `if constexpr` replace most of it.

!!! tip "Pro tip"
    Use `std::forward<Args>(args)...` to pass a pack along unchanged — that's perfect forwarding, the next
    lesson.
""",
files={"": r'''
#include <array>
#include <cstddef>
#include <iostream>
#include <string>
#include <vector>

template <std::size_t N>
struct Fixed { std::array<char, N> buf{}; };

template <auto Value>                                  // auto NTTP
constexpr auto twice = Value * 2;

template <std::size_t N>
struct Name {                                          // structural type usable as an NTTP (C++20)
    char chars[N]{};
    constexpr Name(const char (&s)[N]) { for (std::size_t i = 0; i < N; ++i) chars[i] = s[i]; }
};
template <Name N>
void hello() { std::cout << "hello from " << N.chars << '\n'; }

template <typename... Args>
auto sum(const Args&... args) { return (0 + ... + args); }       // binary left fold, safe if empty

template <typename... Args>
void log(const Args&... args) {
    std::cout << '[' << sizeof...(Args) << " args] ";
    ((std::cout << args << ' '), ...);                              // comma fold
    std::cout << '\n';
}

template <typename T, typename... Args>
bool all_equal(const T& first, const Args&... rest) { return ((first == rest) && ...); }

template <template <typename...> class Container>                 // template template parameter
Container<int> make_ints() { return Container<int>{1, 2, 3}; }

int main() {
    std::cout << sizeof(Fixed<16>) << ' ' << twice<21> << '\n';
    hello<"nttp">();
    std::cout << sum() << ' ' << sum(1, 2, 3) << ' ' << sum(0.5, 1, 2u) << '\n';
    log("rate", 48000, 'k', 1.5);
    std::cout << std::boolalpha << all_equal(3, 3, 3) << ' ' << all_equal(3, 3, 4) << '\n';
    auto v = make_ints<std::vector>();
    std::cout << v.size() << '\n';
}
'''},
takeaways=["Templates can take values (NTTPs), including `auto` and, in C++20, structural class types.",
"`typename... Args` declares a pack; `sizeof...` counts it; `args...` expands it.",
"Fold expressions apply an operator across a pack; the comma fold means 'for each'.",
"Use an initial value in folds when the pack may be empty."],
quiz=[("What does `(0 + ... + args)` evaluate to with no arguments?", "`0` — the initial value; without it, an empty `+` fold is ill-formed."),
("How do you count the elements of a parameter pack?", "`sizeof...(Args)` (or `sizeof...(args)`)."),
("Since C++20, what kinds of class types can be NTTPs?", "Structural types: literal class types whose bases and non-static members are all public and non-mutable (and themselves structural).")]),

dict(title="Forwarding references and perfect forwarding", std="C++20", minutes=10, area="Templates & generic programming",
features=[("Forwarding (universal) references `T&&`", "C++11"), ("Reference collapsing", "C++11"), ("`std::forward`", "C++11"), ("`decltype(auto)` return types", "C++14"), ("Perfect forwarding of packs (`emplace`, `make_unique`)", "C++11")],
why="""
Write a function `make_logged<T>(args...)` that constructs a `T` and logs it. If you take the arguments by
`const&`, you force copies of temporaries — moving becomes impossible. If you take them by `&&`, you can't
pass lvalues. You want to pass every argument *exactly as it came in*. That's perfect forwarding.
""",
body="""
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

{{ex}}

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
""",
files={"": r'''
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

struct Track {
    std::string title;
    explicit Track(const std::string& t) : title{t} { std::cout << "  Track(copy title)\n"; }
    explicit Track(std::string&& t) : title{std::move(t)} { std::cout << "  Track(move title)\n"; }
};

template <typename T, typename... Args>
std::unique_ptr<T> make_logged(Args&&... args) {
    std::cout << "make_logged with " << sizeof...(Args) << " arg(s)\n";
    return std::make_unique<T>(std::forward<Args>(args)...);     // perfect forwarding
}

template <typename T>
void bad_wrapper(T&& x) { Track t{x}; }                           // always an lvalue -> copy

template <typename Container>
decltype(auto) first(Container& c) { return c[0]; }              // returns a reference

template <typename T>
void show(T&&) {
    std::cout << (std::is_lvalue_reference_v<T> ? "  T is an lvalue reference\n" : "  T is a non-reference\n");
}

int main() {
    std::string name = "Blue in Green";
    auto a = make_logged<Track>(name);                 // lvalue: copy
    auto b = make_logged<Track>(std::string{"So What"}); // rvalue: move
    std::cout << "bad_wrapper with an rvalue:\n";
    bad_wrapper(std::string{"Freddie Freeloader"});    // copies anyway
    show(name);
    show(std::string{"tmp"});

    std::vector<int> v{1, 2, 3};
    first(v) = 100;                                    // decltype(auto) kept int&
    std::cout << "v[0]=" << v[0] << ", name still \"" << name << "\"\n";
}
'''},
takeaways=["`T&&` with deduced `T` is a forwarding reference; it binds to lvalues and rvalues.",
"Reference collapsing: any `&` wins; only `&& &&` stays `&&`.",
"`std::forward<T>(x)` preserves the original value category; use it exactly once per argument.",
"`decltype(auto)` preserves references in return types."],
quiz=[("Is `void f(std::vector<T>&& v)` a forwarding reference?", "No — only plain `T&&` with `T` deduced is a forwarding reference; `std::vector<T>&&` is an rvalue reference."),
("What is `T` when you call `template<class T> void f(T&&)` with an lvalue `int x`?", "`T = int&`, so the parameter type collapses to `int&`."),
("Why is `std::move(x)` wrong inside a forwarding function?", "It would move from the caller's lvalues too, leaving their objects in a moved-from state unexpectedly.")]),

dict(title="Type traits, if constexpr, and SFINAE", std="C++20", minutes=12, area="Templates & generic programming",
features=[("`<type_traits>` queries and transformations", "C++11"), ("`_v` and `_t` helpers", "C++14/17"), ("`if constexpr`", "C++17"), ("SFINAE and `std::enable_if`", "C++11"), ("`std::void_t` detection idiom", "C++17"), ("`std::declval`", "C++11"), ("`std::conditional`, `std::decay`, `std::remove_cvref`", "C++11/20")],
why="""
Sometimes a generic function must do different things for different types: serialize integers as
big-endian bytes, floats as IEEE bits, strings as length + characters. `<type_traits>` lets you *ask
questions about types* at compile time, and `if constexpr` lets you branch on the answers — with the
discarded branch never even compiled.
""",
body="""
## Asking questions about types

```cpp
std::is_integral_v<T>            // true for int, char, bool...
std::is_trivially_copyable_v<T>  // safe to memcpy?
std::is_same_v<T, U>
std::remove_cvref_t<T>           // strip const, volatile and references (C++20)
std::conditional_t<B, X, Y>      // pick a type
```

`_v` gives a value, `_t` gives a type.

## `if constexpr` (C++17)

```cpp
if constexpr (std::is_integral_v<T>) { ... }   // other branch is discarded at compile time
```

With plain `if`, *both* branches must compile for every `T`. With `if constexpr`, the discarded branch
isn't instantiated — so it may contain code that's invalid for this `T`.

{{ex}}

## SFINAE: the old way to constrain templates

"Substitution Failure Is Not An Error": if substituting `T` into a template's *signature* fails, that
overload is silently removed instead of causing an error. Pre-C++20 code used this with `std::enable_if`:

```cpp
template <typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
void encode(T value);
```

And the **detection idiom** with `std::void_t` checks whether an expression is valid ("does `T` have a
`.size()`?"). It works, but it's cryptic. In C++20, **concepts** (next week) replace almost all of it. You
need to *read* SFINAE; you rarely need to write it any more.

!!! tip "Pro tip: `static_assert` your assumptions"
    `static_assert(std::is_trivially_copyable_v<Header>);` next to a `memcpy` turns a silent future bug into
    a compile error.
""",
files={"": r'''
#include <bit>
#include <cstdint>
#include <iostream>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

template <typename T>
void encode(std::vector<std::uint8_t>& out, const T& value) {
    using U = std::remove_cvref_t<T>;
    if constexpr (std::is_same_v<U, bool>) {
        out.push_back(value ? 1 : 0);
    } else if constexpr (std::is_integral_v<U>) {          // big-endian bytes
        for (int i = sizeof(U) - 1; i >= 0; --i) out.push_back(static_cast<std::uint8_t>(value >> (8 * i)));
    } else if constexpr (std::is_floating_point_v<U>) {
        using Bits = std::conditional_t<sizeof(U) == 4, std::uint32_t, std::uint64_t>;
        encode(out, std::bit_cast<Bits>(value));
    } else if constexpr (std::is_same_v<U, std::string>) {
        encode(out, static_cast<std::uint16_t>(value.size()));
        out.insert(out.end(), value.begin(), value.end());
    } else {
        static_assert(sizeof(U) == 0, "encode: unsupported type");   // fires only if instantiated
    }
}

// Pre-C++20 detection idiom: does T have .size()?
template <typename, typename = void> struct has_size : std::false_type {};
template <typename T> struct has_size<T, std::void_t<decltype(std::declval<const T&>().size())>> : std::true_type {};

// Pre-C++20 SFINAE overloads
template <typename T, std::enable_if_t<has_size<T>::value, int> = 0>
std::size_t length(const T& t) { return t.size(); }
template <typename T, std::enable_if_t<!has_size<T>::value, int> = 0>
std::size_t length(const T&) { return 1; }

int main() {
    std::vector<std::uint8_t> bytes;
    encode(bytes, std::uint16_t{0x1234});
    encode(bytes, true);
    encode(bytes, 1.0f);
    encode(bytes, std::string{"hi"});
    std::cout << std::hex;
    for (auto b : bytes) std::cout << static_cast<int>(b) << ' ';
    std::cout << std::dec << '\n';

    std::cout << "has_size<string>=" << has_size<std::string>::value
              << " has_size<int>=" << has_size<int>::value << '\n';
    std::cout << length(std::string{"abc"}) << ' ' << length(42) << '\n';
    static_assert(std::is_trivially_copyable_v<float>);
}
'''},
takeaways=["Type traits answer questions (`is_integral_v`) and transform types (`remove_cvref_t`) at compile time.",
"`if constexpr` discards the untaken branch, so it can contain code invalid for that type.",
"SFINAE/`enable_if`/`void_t` are the pre-C++20 constraint tools — read them, prefer concepts for new code.",
"`static_assert` documents and enforces type assumptions."],
quiz=[("Why can't a plain `if` replace `if constexpr` in `encode`?", "Both branches of a plain `if` must compile for every `T`; e.g. `value >> 8` doesn't compile for `std::string`."),
("Why does `static_assert(sizeof(U) == 0, ...)` not fire for supported types?", "It's in a discarded `if constexpr` branch of a template and depends on `U`, so it's only evaluated when that branch is instantiated."),
("What does SFINAE stand for and what does it do?", "Substitution Failure Is Not An Error: when substituting template arguments into a signature fails, that candidate is dropped from overload resolution instead of causing a hard error.")]),
],
assignment=dict(title="A generic binary serializer", task="""
Write `template <typename... Ts> std::vector<std::uint8_t> pack(const Ts&... values)` that serializes every
argument in order: integers big-endian, `bool` as one byte, floating-point via `std::bit_cast`, `std::string`
as a 16-bit length then bytes. Also write `std::string hex(const std::vector<std::uint8_t>&)`.

Unsupported types must be a compile-time error with a readable message.
""", starter=r'''
#include <cstdint>
#include <string>
#include <vector>

template <typename... Ts>
std::vector<std::uint8_t> pack(const Ts&... values) {
    std::vector<std::uint8_t> out;
    // TODO: fold over values, encoding each
    return out;
}

int main() { return static_cast<int>(pack(1, 2).size()); }
''', solution=r'''
#include <bit>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <string>
#include <type_traits>
#include <vector>

template <typename T>
void put(std::vector<std::uint8_t>& out, const T& v) {
    using U = std::remove_cvref_t<T>;
    if constexpr (std::is_same_v<U, bool>) out.push_back(v ? 1 : 0);
    else if constexpr (std::is_integral_v<U>) {
        using UU = std::make_unsigned_t<U>;
        const auto u = static_cast<UU>(v);
        for (int i = sizeof(U) - 1; i >= 0; --i) out.push_back(static_cast<std::uint8_t>(u >> (8 * i)));
    } else if constexpr (std::is_floating_point_v<U>) {
        using Bits = std::conditional_t<sizeof(U) == 4, std::uint32_t, std::uint64_t>;
        put(out, std::bit_cast<Bits>(v));
    } else if constexpr (std::is_same_v<U, std::string>) {
        put(out, static_cast<std::uint16_t>(v.size()));
        out.insert(out.end(), v.begin(), v.end());
    } else {
        static_assert(sizeof(U) == 0, "pack: unsupported type");
    }
}

template <typename... Ts>
std::vector<std::uint8_t> pack(const Ts&... values) {
    std::vector<std::uint8_t> out;
    (put(out, values), ...);
    return out;
}

std::string hex(const std::vector<std::uint8_t>& bytes) {
    std::string s;
    char buf[4];
    for (auto b : bytes) { std::snprintf(buf, sizeof buf, "%02x ", b); s += buf; }
    return s;
}

int main() {
    std::cout << hex(pack(std::int16_t{-2}, true, std::string{"ok"}, 1.5f)) << '\n';
    std::cout << hex(pack()) << "(empty)\n";
}
'''))
