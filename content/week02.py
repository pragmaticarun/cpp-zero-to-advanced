WEEK = dict(num=2, title="Control flow, functions, references, scope", intro="""
This week we learn to structure programs: making decisions, looping, splitting work into functions,
and passing data around efficiently with references. We'll finish with how long objects live and how
namespaces, enums and structs help organize code.

By Friday you'll be able to write small but real programs — and you'll understand *where* each object
lives in memory and *when* it dies, which is the single most important mental model in C++.
""", lessons=[
dict(title="Control flow: if, switch, loops, and range-for", std="C++20", minutes=9, area="Basics: control flow & functions",
features=[("if / else, switch, fallthrough and `[[fallthrough]]`", "C++17"), ("`if` and `switch` with initializer", "C++17"), ("while, do-while, for, break, continue", "C++98"), ("Range-based for, with initializer", "C++20"), ("Conditional operator `?:`", "C++98")],
why="""
Imagine scanning a buffer of audio samples looking for the first one that clips. You need to loop, test
each value, and stop early. That's control flow, and C++ has a few modern touches — like declaring a
variable right inside an `if` — that make such code tighter and safer. Let's go through them quickly.
""",
body="""
## `if` and the `if`-with-initializer

You've seen `if (cond) { ... } else { ... }`. Since C++17 you can put a declaration *inside* the `if`:

```cpp
if (auto it = settings.find("volume"); it != settings.end()) {
    use(it->second);
}   // `it` is out of scope here: it can't be misused later
```

The variable lives only as long as the `if`/`else`. Small scopes are a great habit: fewer names in play,
fewer chances to use a stale one.

## `switch`

`switch` works on integers and enums. Each `case` *falls through* to the next unless you `break`.
Accidental fallthrough is a classic bug, so compilers warn (`-Wimplicit-fallthrough`). When you
*mean* it, say so with `[[fallthrough]];`.

## Loops

```cpp
for (int i = 0; i < n; ++i) { ... }   // classic counted loop
while (cond) { ... }                  // test first
do { ... } while (cond);              // run at least once
for (const auto& x : container) { ... }   // range-based for (C++11)
```

Range-based `for` is the default for "do something with each element". Use `const auto&` to avoid
copying each element; use `auto&` if you want to modify them.

C++20 added an initializer to range-for too: `for (auto v = make(); auto x : v)`.

Here's everything together, finding the first clipped sample:

{{ex}}

## A common mistake: modifying a copy

```cpp
for (auto s : samples) s *= 0.5f;   // WRONG: halves a copy; samples unchanged
for (auto& s : samples) s *= 0.5f;  // right
```

!!! tip "Pro tip"
    Before writing a loop, ask: "is there an algorithm for this?" Finding the first matching element is
    `std::ranges::find_if`. We'll do a full tour of algorithms in Week 11 — loops are still fine for now.
""",
files={"": r'''
#include <iostream>
#include <vector>

enum class Level { quiet, normal, loud, clipping };

Level classify(float s) {
    const float a = s < 0 ? -s : s;   // conditional operator
    if (a >= 1.0f) return Level::clipping;
    if (a > 0.7f) return Level::loud;
    if (a > 0.1f) return Level::normal;
    return Level::quiet;
}

int main() {
    std::vector<float> samples{0.05f, 0.4f, -0.8f, 1.2f, 0.3f};

    int index = 0;
    for (const auto& s : samples) {
        if (const Level l = classify(s); l == Level::clipping) {   // if with initializer
            std::cout << "first clip at index " << index << '\n';
            break;
        }
        ++index;
    }

    for (auto& s : samples) s *= 0.5f;   // auto& modifies the elements

    for (std::size_t i = 0; i < samples.size(); ++i) {
        switch (classify(samples[i])) {
        case Level::clipping:
            std::cout << "C";
            [[fallthrough]];          // deliberate: clipping is also "loud"
        case Level::loud:   std::cout << "L "; break;
        case Level::normal: std::cout << "n "; break;
        case Level::quiet:  std::cout << ". "; break;
        }
    }
    std::cout << '\n';
}
'''},
takeaways=["Use `if (init; cond)` to keep helper variables scoped to the `if`.",
"`switch` cases fall through without `break`; mark intentional fallthrough with `[[fallthrough]]`.",
"Range-for with `const auto&` reads without copying; `auto&` modifies in place."],
quiz=[("What's wrong with `for (auto x : v) x = 0;`?", "`x` is a copy of each element, so the vector is unchanged. Use `auto& x`."),
("Where is `it` visible in `if (auto it = m.find(k); it != m.end()) {...} else {...}`?", "In the condition, the `if` body *and* the `else` body, but not after the whole statement."),
("Why does the compiler warn about a `case` without `break`?", "Implicit fallthrough is a common bug. `[[fallthrough]];` documents that it's intentional and silences the warning.")]),

dict(title="Functions, overloading and default arguments", std="C++20", minutes=10, area="Basics: control flow & functions",
features=[("Function declarations, definitions, return types, trailing return type", "C++11"), ("Function overloading and overload resolution basics", "C++98"), ("Default arguments", "C++98"), ("`auto` return type deduction", "C++14"), ("Abbreviated function templates (`auto` parameters)", "C++20"), ("`inline` functions", "C++98"), ("Recursion", "C++98")],
why="""
As soon as a program does more than one thing, you want to name each thing. Functions are names for
behaviour. C++ adds two conveniences you may not have in C: **overloading** (several functions with the
same name but different parameters) and **default arguments**. They're handy — and they have a couple of
sharp corners we'll walk through.
""",
body="""
## Anatomy

```cpp
int add(int a, int b) { return a + b; }       // classic
auto add(double a, double b) -> double;        // trailing return type (C++11), same meaning
auto twice(int x) { return 2 * x; }            // return type deduced (C++14): int
```

Most of the time, write the return type explicitly for public functions (it's documentation) and use
deduced `auto` for short local helpers.

## Overloading

You can have several functions with the same name if their parameter lists differ. The compiler picks the
**best match** for each call — that's *overload resolution*. Roughly: an exact match beats a promotion,
which beats a conversion.

{{ex}}

Notice `describe(2.5f)`: there's no `float` overload, but `float → double` is a *promotion*, which beats
`float → int` (a conversion). And `describe('x')`: `char → int` is a promotion, so it calls `describe(int)`.

## The ambiguous call (the wrong way)

```cpp
void f(long);
void f(double);
f(42);   // ERROR: ambiguous. int->long and int->double are both conversions
```

When this happens, either add an exact overload or make the call explicit (`f(42L)`).

## Default arguments

```cpp
void log(const std::string& msg, int level = 1);
log("hi");        // level = 1
log("oops", 3);
```

Defaults go in the **declaration** (usually the header), not repeated in the definition. They're
substituted at the *call site* — so changing a default in a header requires recompiling the callers, a
subtle point if you ship shared libraries.

!!! warning "Common pitfall: defaults + overloads"
    `void f(int x, int y = 0);` and `void f(int x);` together make `f(1)` ambiguous. Pick one tool.

## Generic functions with `auto` parameters (C++20)

```cpp
auto largest(auto a, auto b) { return a > b ? a : b; }
```

This is an *abbreviated function template*: a template in disguise. We'll unpack templates in Week 7;
for now just know it works for any types that support `>`.
""",
files={"": r'''
#include <iostream>
#include <string>

void describe(int x)                { std::cout << "int " << x << '\n'; }
void describe(double x)             { std::cout << "double " << x << '\n'; }
void describe(const std::string& s) { std::cout << "string \"" << s << "\"\n"; }

// Default argument
std::string pad(const std::string& s, std::size_t width = 8, char fill = '.') {
    if (s.size() >= width) return s;
    return s + std::string(width - s.size(), fill);
}

// Deduced return type and an abbreviated function template (C++20)
auto square(int x) { return x * x; }
auto largest(auto a, auto b) { return a > b ? a : b; }

// Recursion
long long factorial(int n) { return n <= 1 ? 1 : n * factorial(n - 1); }

int main() {
    describe(42);
    describe(2.5f);                  // float -> double is a promotion
    describe('x');                   // char -> int is a promotion
    describe(std::string{"hello"});
    std::cout << '[' << pad("abc") << "] [" << pad("abc", 5, '-') << "]\n";
    std::cout << square(7) << ' ' << largest(3, 9) << ' ' << largest(2.5, 1.5) << '\n';
    std::cout << "20! = " << factorial(20) << '\n';
}
'''},
takeaways=["Overload resolution prefers exact matches, then promotions, then conversions; ties are errors.",
"Put default arguments in the declaration; they're filled in at the call site.",
"`auto` return types are deduced; `auto` parameters (C++20) make a function template."],
quiz=[("Given `void f(int); void f(double);`, which is called by `f('a')`? By `f(1.0f)`?", "`f(int)` (char→int is an integral promotion) and `f(double)` (float→double is a floating-point promotion)."),
("Why might changing a default argument in a library header not affect an already-compiled app?", "Defaults are inserted at each call site at compile time, so the app keeps the old value until recompiled."),
("What does `auto f(auto x)` declare?", "An abbreviated function template (C++20): equivalent to `template<class T> auto f(T x)`.")]),

dict(title="References, const, and how to pass parameters", std="C++20", minutes=11, area="Basics: control flow & functions",
features=[("Lvalue references `T&`", "C++98"), ("const references bind to temporaries (lifetime extension)", "C++98"), ("Parameter passing guidelines: by value, `const T&`, `T&`", "—"), ("`auto` deduction drops references and top-level const; `auto&`, `const auto&`", "C++11"), ("Dangling references", "C++98")],
why="""
Suppose a function processes a 10 MB video frame stored in a `std::vector<std::uint8_t>`. If you
write `void process(std::vector<std::uint8_t> frame)`, every call copies 10 MB. Change one character —
`const std::vector<std::uint8_t>& frame` — and the copy disappears. References are how C++ lets you
refer to an existing object without copying it. Let's build the intuition.
""",
body="""
## A reference is another name for an existing object

```cpp
int volume = 5;
int& v = volume;   // v *is* volume, under another name
v = 7;             // volume is now 7
```

A reference must be initialized, and it can never be "re-seated" to refer to something else. Assigning
to it assigns to the object it refers to.

## Three ways to pass a parameter

| You want to... | Write | Why |
|---|---|---|
| read a cheap value (`int`, `double`, small struct) | `void f(int x)` | copying a few bytes is the fastest thing there is |
| read an expensive object | `void f(const std::string& s)` | no copy, can't modify |
| modify the caller's object | `void f(std::string& s)` | caller sees the change |

(There's a fourth — `T&&` — for "I want to steal from a temporary". That's Week 5's move semantics.)

{{ex}}

## `const T&` binds to temporaries

`print_twice(std::string{"temp"})` works even though the argument is a temporary: a `const` reference may
bind to a temporary, and the temporary lives until the end of the full expression. A *non-const*
reference can't bind to a temporary — that would let you modify a value that's about to disappear.

## `auto` and references

`auto` deduces a *value* type: it strips references and top-level `const`.

```cpp
const std::string& name = get_name();
auto a = name;          // std::string — a copy!
const auto& b = name;   // const std::string& — no copy
```

So when you want a reference, ask for one: `auto&` or `const auto&`.

## The big danger: dangling references

A reference doesn't keep its object alive. Returning a reference to a local is the classic mistake:

```cpp
const std::string& make_label() {
    std::string s = "label";
    return s;          // WRONG: s is destroyed when the function returns
}                      // the caller gets a dangling reference -> UB
```

Compilers warn about this simple case (`-Wreturn-local-addr` / `-Wreturn-stack-address`), but subtler
versions — references into a vector that later reallocates, for example — need you to think about
**lifetime**. That's next lesson.

!!! tip "Pro tip"
    Return by value. Thanks to copy elision and move semantics (Week 5), returning a `std::string` or
    `std::vector` by value is cheap. Return references only to things that clearly outlive the call
    (like a member of `*this`).
""",
files={"": r'''
#include <iostream>
#include <string>
#include <vector>

double average(const std::vector<int>& v) {   // read-only, no copy
    if (v.empty()) return 0.0;
    long long sum = 0;
    for (int x : v) sum += x;
    return static_cast<double>(sum) / static_cast<double>(v.size());
}

void normalize(std::vector<int>& v, int maxValue) {  // modifies the caller's vector
    for (int& x : v) x = x > maxValue ? maxValue : x;
}

void print_twice(const std::string& s) { std::cout << s << ' ' << s << '\n'; }

int main() {
    int volume = 5;
    int& alias = volume;
    alias = 7;
    std::cout << "volume=" << volume << '\n';

    std::vector<int> levels{3, 9, 12, 4};
    normalize(levels, 10);
    std::cout << "average=" << average(levels) << '\n';

    print_twice(std::string{"temp"});   // const& binds to a temporary

    const std::string& ref = levels.size() > 2 ? std::string{"many"} : std::string{"few"};
    auto copy = ref;            // auto drops the reference: std::string copy
    const auto& same = ref;     // keeps the reference
    std::cout << copy << ' ' << same << ' ' << std::boolalpha << (&same == &ref) << '\n';
}
'''},
takeaways=["A reference is an alias for an existing object; it must be initialized and can't be re-seated.",
"Pass cheap types by value, expensive ones by `const&`, and use `&` only to modify the caller's object.",
"`auto` deduces a value type; write `const auto&` when you want a reference.",
"References don't extend lifetimes (except a const& bound directly to a temporary) — beware dangling."],
quiz=[("Why can't `void f(std::string& s)` be called as `f(std::string{\"x\"})`?", "A non-const lvalue reference can't bind to a temporary (an rvalue). Use `const std::string&` (or `std::string&&` / by value if you want to consume it)."),
("Given `const std::vector<int>& r = v;`, what is the type of `auto x = r;`?", "`std::vector<int>` — a full copy, because `auto` drops the reference and top-level const."),
("Is it fine to pass an `int` by `const int&`?", "It works, but by value is simpler and usually faster: an `int` fits in a register; a reference may force it into memory and introduces aliasing questions.")]),

dict(title="Scope, lifetime, storage duration and namespaces", std="C++20", minutes=12, area="Basics: control flow & functions",
features=[("Block scope and name hiding", "C++98"), ("Object lifetime; destruction in reverse order", "C++98"), ("Storage duration: automatic, static, thread, dynamic", "C++11"), ("Function-local `static` (thread-safe init)", "C++11"), ("Namespaces, nested namespaces `a::b::c`, inline namespaces", "C++17"), ("`using` declarations vs `using namespace`", "C++98"), ("Static initialization order fiasco", "—")],
why="""
Every bug involving a dangling pointer or a use-after-free comes down to one question: *when does this
object die?* In garbage-collected languages you rarely ask it. In C++ you get to decide — which is where
the performance (and the deterministic cleanup!) comes from. This lesson gives you the rules.
""",
body="""
## Scope vs lifetime

- **Scope** is where a *name* is visible in the source code.
- **Lifetime** is when an *object* exists at run time.

They often coincide for local variables, but not always (a reference's name can outlive the object it
refers to — that's a dangling reference).

## The four storage durations

| Storage duration | Examples | Lives... |
|---|---|---|
| automatic | local variables, parameters | from its definition until the end of its block |
| static | globals, `static` locals, `static` members | for the whole program (locals: from first use) |
| thread | `thread_local` variables | for the lifetime of the thread (Week 13) |
| dynamic | `new`/`delete`, owned by smart pointers | until you (or a smart pointer) free it |

Automatic objects are destroyed **in reverse order of construction** when their block ends. That's
deterministic, and it's the foundation of RAII (Week 4). Let's watch it happen:

{{ex}}

Look at the order: `outer` constructed, then `inner`; at the closing brace `inner` dies *first*.
The function-local `static` is constructed the first time `counter()` runs and destroyed after `main` returns.

## Function-local statics

Since C++11, initializing a function-local `static` is **thread-safe**: if two threads call the function
at once, one initializes and the other waits. This makes "construct on first use" a safe singleton pattern
and is the cure for the *static initialization order fiasco*: globals in different translation units are
initialized in an unspecified order, so one global constructor must never depend on another TU's global.

## Namespaces

Namespaces prevent name clashes between libraries:

```cpp
namespace media::audio {        // nested namespace definition, C++17
    int sample_rate();
}
media::audio::sample_rate();
```

`using media::audio::sample_rate;` brings in one name. `using namespace std;` brings in *everything*;
fine in a small `.cpp`, but **never in a header** — you'd be forcing it on everyone who includes you.

**Inline namespaces** are a versioning tool: `namespace lib { inline namespace v2 { ... } }` makes
`lib::f` refer to `lib::v2::f`, while the mangled symbol includes `v2`. The standard library uses this
for ABI versioning (e.g. libc++'s `std::__1`).

!!! warning "Common pitfall: shadowing"
    An inner variable with the same name hides the outer one. `-Wshadow` warns about it. A renamed loop
    counter that silently shadows a member variable can take hours to find.
""",
files={"": r'''
#include <iostream>
#include <string>

struct Noisy {
    std::string name;
    explicit Noisy(std::string n) : name(std::move(n)) { std::cout << "  construct " << name << '\n'; }
    ~Noisy() { std::cout << "  destroy   " << name << '\n'; }
};

namespace media::audio {           // C++17 nested namespace
int counter() {
    static Noisy once{"static-local"};  // constructed on first call only
    static int calls = 0;
    return ++calls;
}
}  // namespace media::audio

Noisy global{"global"};            // static storage: before main, destroyed after main

int main() {
    std::cout << "main starts\n";
    Noisy outer{"outer"};
    {
        Noisy inner{"inner"};
        const int n = media::audio::counter();   // first call constructs the static
        std::cout << "  calls=" << n << '\n';
    }   // inner destroyed here
    using media::audio::counter;
    std::cout << "  calls=" << counter() << '\n';
    std::cout << "main ends\n";
}   // outer destroyed here; then static-local, then global (reverse order)
'''},
takeaways=["Scope is about names; lifetime is about objects.",
"Automatic objects die at the end of their block, in reverse order of construction.",
"Function-local statics are initialized on first use, thread-safely (C++11).",
"Never put `using namespace` in a header; use nested namespaces `a::b` (C++17)."],
quiz=[("In what order are three local objects `a`, `b`, `c` destroyed?", "`c`, `b`, `a` — reverse order of construction."),
("What is the static initialization order fiasco and one fix?", "Globals in different translation units are initialized in unspecified order, so one global's constructor may use another before it's initialized. Fix: replace the global with a function returning a reference to a function-local static (construct on first use), or use `constinit`/`constexpr` for constant initialization."),
("Why is `using namespace std;` in a header bad?", "Every file including the header gets all of `std` dumped into the global namespace, which can cause ambiguities and silently change overload resolution.")]),

dict(title="Enums, structs and attributes", std="C++23", minutes=10, area="Basics: types & values",
features=[("Unscoped `enum` vs scoped `enum class`, underlying type", "C++11"), ("`using enum`", "C++20"), ("`std::to_underlying`", "C++23"), ("`struct` basics, default member initializers", "C++11"), ("Attributes: `[[nodiscard]]`, `[[maybe_unused]]`, `[[deprecated]]`, `[[noreturn]]`", "C++17"), ("`[[likely]]` / `[[unlikely]]`, `[[no_unique_address]]`", "C++20"), ("`[[assume]]`", "C++23")],
why="""
Here's a function signature from a real codebase: `open_stream(int, int, bool, bool)`. What does
`open_stream(2, 1, true, false)` mean? Nobody knows without reading the docs. Enums and structs let you
give *meaning* to values, and the compiler then checks that meaning for you. Attributes let you tell the
compiler (and readers) even more. Let's make that call readable.
""",
body="""
## Old enums leak and convert

```cpp
enum Color { red, green };       // unscoped: `red` is a global name
enum Fruit { apple, orange };
int x = red + apple;             // compiles! nonsense, but legal (and warns)
```

## `enum class`: scoped and strongly typed (C++11)

```cpp
enum class Codec : std::uint8_t { aac, opus, flac };   // explicit underlying type
Codec c = Codec::opus;          // must qualify
// int n = c;                   // ERROR: no implicit conversion
auto n = std::to_underlying(c); // C++23; or static_cast<std::uint8_t>(c)
```

Always prefer `enum class`. In C++20, `using enum Codec;` inside a `switch` saves you typing
`Codec::` on every case.

## Structs group data

```cpp
struct StreamConfig {
    Codec codec = Codec::aac;   // default member initializers (C++11)
    int sample_rate = 48'000;
    int channels = 2;
    bool low_latency = false;
};
```

Now `open_stream(StreamConfig{.codec = Codec::opus, .low_latency = true})` reads like documentation.
(Those `.name =` *designated initializers* are C++20; Week 5 covers them in detail.)

## Attributes

Attributes are annotations in `[[double brackets]]`:

| Attribute | Meaning |
|---|---|
| `[[nodiscard]]` (C++17; with reason C++20) | warn if the caller ignores the return value |
| `[[maybe_unused]]` | silence unused warnings |
| `[[deprecated("use X")]]` (C++14) | warn on use |
| `[[noreturn]]` (C++11) | function never returns (e.g. calls `std::abort`) |
| `[[fallthrough]]` (C++17) | intentional switch fallthrough |
| `[[likely]]` / `[[unlikely]]` (C++20) | branch hints for the optimizer |
| `[[no_unique_address]]` (C++20) | an empty member may take no space |
| `[[assume(expr)]]` (C++23) | the optimizer may assume `expr` is true — UB if it isn't! |

{{ex}}

`[[nodiscard]]` is the one to adopt immediately. Put it on functions where ignoring the result is almost
certainly a bug: error codes, `empty()`-style queries, factory functions.

!!! warning "Be careful with `[[likely]]` and `[[assume]]`"
    Measure before adding branch hints; the compiler and CPU predictor are usually good already.
    `[[assume]]` is a promise: if it's ever false, you have undefined behaviour.
""",
files={"": r'''
#include <cstdint>
#include <iostream>
#include <string_view>
#include <utility>

enum class Codec : std::uint8_t { aac, opus, flac };

struct StreamConfig {
    Codec codec = Codec::aac;
    int sample_rate = 48'000;
    int channels = 2;
    bool low_latency = false;
};

std::string_view name(Codec c) {
    switch (c) {
        using enum Codec;            // C++20: no need to write Codec:: below
        case aac:  return "AAC";
        case opus: return "Opus";
        case flac: return "FLAC";
    }
    return "?";
}

[[nodiscard]] bool open_stream(const StreamConfig& cfg) {
    if (cfg.channels <= 0) [[unlikely]] return false;
    std::cout << "open " << name(cfg.codec) << " @" << cfg.sample_rate << "Hz x"
              << cfg.channels << (cfg.low_latency ? " low-latency" : "") << '\n';
    return true;
}

struct Empty {};
struct WithTag {
    int value;
    [[no_unique_address]] Empty tag;   // takes no extra space
};

int main() {
    const bool ok = open_stream({.codec = Codec::opus, .low_latency = true});
    [[maybe_unused]] const bool ignored = open_stream(StreamConfig{});
    std::cout << "ok=" << ok << " underlying(flac)=" << int{std::to_underlying(Codec::flac)}
              << " sizeof(WithTag)=" << sizeof(WithTag) << '\n';
}
''', "_bad": {"expect": "fail", "code": r'''
// Wrong way: scoped enums don't convert implicitly to int.
enum class Codec { aac, opus };
int main() {
    int n = Codec::opus;   // error: cannot convert 'Codec' to 'int'
    return n;
}
'''}},
takeaways=["Prefer `enum class` (scoped, no implicit conversions, explicit underlying type).",
"Use structs with default member initializers to replace long lists of `int`/`bool` parameters.",
"`[[nodiscard]]` turns ignored error results into compiler warnings — use it generously.",
"`[[assume]]` and `[[likely]]` are optimization hints; `[[assume]]` is UB if false."],
quiz=[("Name two problems with unscoped enums that `enum class` fixes.", "Unscoped enumerators leak into the enclosing scope (name clashes), and they implicitly convert to `int` (allowing nonsense arithmetic/comparisons between unrelated enums)."),
("How do you get the integer value of an `enum class` in C++23?", "`std::to_underlying(e)` from `<utility>` (or `static_cast<std::underlying_type_t<E>>(e)` before C++23)."),
("What happens if the condition in `[[assume(x > 0)]]` is false at run time?", "Undefined behaviour. The optimizer was allowed to rely on it.")]),
],
assignment=dict(title="A tiny command-line unit converter", task="""
Write a program that converts between units of audio level and time:

- `enum class Unit { ms, samples, seconds }` with a `[[nodiscard]] double convert(double value, Unit from, Unit to, int sample_rate = 48000)` function.
- Overload a `print` function for `double` and for a `struct Result { double value; Unit unit; }`.
- Use `const&` parameters for anything that isn't a cheap scalar.
- Process a fixed list of test conversions in `main` with a range-for loop and print the results.

Compile warning-free. Bonus: use a `switch` with `using enum Unit;`.
""", solution=r'''
#include <iostream>
#include <string_view>
#include <vector>

enum class Unit { ms, samples, seconds };

std::string_view suffix(Unit u) {
    switch (u) {
        using enum Unit;
        case ms:      return "ms";
        case samples: return "samples";
        case seconds: return "s";
    }
    return "?";
}

[[nodiscard]] double to_seconds(double v, Unit u, int rate) {
    switch (u) {
        using enum Unit;
        case ms:      return v / 1000.0;
        case samples: return v / rate;
        case seconds: return v;
    }
    return 0.0;
}

[[nodiscard]] double convert(double value, Unit from, Unit to, int sample_rate = 48000) {
    const double s = to_seconds(value, from, sample_rate);
    switch (to) {
        using enum Unit;
        case ms:      return s * 1000.0;
        case samples: return s * sample_rate;
        case seconds: return s;
    }
    return 0.0;
}

struct Result { double value; Unit unit; };

void print(double v) { std::cout << v; }
void print(const Result& r) { print(r.value); std::cout << ' ' << suffix(r.unit) << '\n'; }

struct Job { double value; Unit from; Unit to; };

int main() {
    const std::vector<Job> jobs{{20, Unit::ms, Unit::samples},
                                {44100, Unit::samples, Unit::seconds},
                                {1.5, Unit::seconds, Unit::ms}};
    for (const auto& j : jobs) {
        print(j.value);
        std::cout << ' ' << suffix(j.from) << " -> ";
        print(Result{convert(j.value, j.from, j.to), j.to});
    }
    std::cout << "at 44.1kHz, 20 ms = " << convert(20, Unit::ms, Unit::samples, 44100) << " samples\n";
}
'''))
