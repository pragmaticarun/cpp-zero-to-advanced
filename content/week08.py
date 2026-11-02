WEEK = dict(num=8, title="Concepts, compile-time programming, and lambdas", intro="""
This week modernizes everything from Week 7. Concepts give templates readable constraints and readable
errors. `constexpr`/`consteval` move work from run time to compile time. Lambdas and type erasure give you
flexible callbacks. We finish with CRTP and C++23's *deducing this*.
""", lessons=[
dict(title="Concepts and requires-clauses", std="C++20", minutes=12, area="Templates & generic programming",
features=[("Concepts (`concept`)", "C++20"), ("`requires` clauses and `requires` expressions", "C++20"), ("Standard concepts (`<concepts>`, iterator/range concepts)", "C++20"), ("Constrained `auto` (`std::integral auto x`)", "C++20"), ("Subsumption / overload ordering by constraints", "C++20")],
why="""
Remember the 200-line template error from Week 7? Concepts fix that. A concept is a *named compile-time
predicate on types*: "T is something you can add and divide". Put it on a template and two things happen:
callers get a one-line error that says which requirement failed, and you can overload templates on
capabilities cleanly — no SFINAE tricks.
""",
body="""
## Using standard concepts

```cpp
#include <concepts>
template <std::integral T> T gcd(T a, T b);
void log_count(std::unsigned_integral auto n);         // constrained auto
```

`<concepts>` provides `std::integral`, `std::floating_point`, `std::same_as`, `std::convertible_to`,
`std::totally_ordered`, `std::invocable`, `std::regular`, ...; `<iterator>` and `<ranges>` add
`std::input_iterator`, `std::ranges::range`, `std::ranges::random_access_range`, and more.

## Writing your own

```cpp
template <typename T>
concept Averageable = requires(T a, T b, std::size_t n) {
    { a + b } -> std::convertible_to<T>;     // expression must compile, result convertible
    { a / n } -> std::convertible_to<T>;
    T{};                                     // default constructible
};
```

A `requires`-expression lists expressions that must be valid. It doesn't evaluate them.

## The payoff: better errors

Call a constrained template with a wrong type and the compiler says "constraints not satisfied" and names
the failed requirement — instead of an error buried deep inside the body.

{{ex}}

## Overloading by constraints

If two overloads both match, the **more constrained** one wins (if one's constraints *subsume* the other's).
That's how the example picks a faster `advance_by` for random-access iterators. Subsumption only works
through named concepts — not through arbitrary boolean expressions — another reason to name your concepts.

!!! tip "Pro tip"
    Constrain on *what you use*, not on what you think the type "is". `requires { a + b }` is better than
    "must be a number" if all you do is add.
""",
files={"": r'''
#include <concepts>
#include <cstddef>
#include <forward_list>
#include <iostream>
#include <iterator>
#include <list>
#include <string>
#include <vector>

template <typename T>
concept Averageable = requires(T a, T b, std::size_t n) {
    { a + b } -> std::convertible_to<T>;
    { a / n } -> std::convertible_to<T>;
    T{};
};

template <Averageable T>
T average(const std::vector<T>& v) {
    T total{};
    for (const auto& x : v) total = total + x;
    return v.empty() ? T{} : total / v.size();
}

template <std::integral T>
T gcd(T a, T b) { while (b != 0) { T t = a % b; a = b; b = t; } return a; }

template <std::input_iterator It>
const char* advance_by(It& it, int n) { while (n-- > 0) ++it; return "step-by-step"; }

template <std::random_access_iterator It>                       // more constrained: wins when it matches
const char* advance_by(It& it, int n) { it += n; return "jump"; }

void print_count(std::unsigned_integral auto n) { std::cout << "count=" << n << '\n'; }

template <typename T>
    requires std::totally_ordered<T> && std::copyable<T>
T largest(T a, T b) { return a < b ? b : a; }

int main() {
    std::cout << average(std::vector<double>{1.0, 2.0, 4.5}) << '\n';
    std::cout << gcd(48, 18) << '\n';

    std::vector<int> v{1, 2, 3, 4, 5};
    std::list<int> l{1, 2, 3, 4, 5};
    auto vi = v.begin();
    auto li = l.begin();
    std::cout << advance_by(vi, 3) << " -> " << *vi << '\n';
    std::cout << advance_by(li, 3) << " -> " << *li << '\n';

    print_count(3u);
    std::cout << largest(std::string{"pear"}, std::string{"apple"}) << '\n';
    static_assert(!Averageable<std::string>);       // no string / size_t
}
''', "_bad": {"expect": "fail", "code": r'''
// A readable error: "constraints not satisfied ... std::integral<double>"
#include <concepts>
template <std::integral T> T gcd(T a, T b) { while (b != 0) { T t = a % b; a = b; b = t; } return a; }
int main() { return static_cast<int>(gcd(4.0, 2.0)); }
'''}},
takeaways=["A concept is a named compile-time predicate; constrain templates with it.",
"`requires` expressions list operations that must compile, optionally with result constraints.",
"Constrained templates produce short, specific errors.",
"When overloads both match, the more constrained one (by subsumption of named concepts) wins."],
quiz=[("What does `{ a + b } -> std::convertible_to<T>;` require?", "That `a + b` is a valid expression and its result type is convertible to `T`."),
("Why did `advance_by` on a `std::vector` iterator choose the \"jump\" version?", "Both overloads match, but `std::random_access_iterator` subsumes `std::input_iterator`, so the more constrained overload wins."),
("Does a `requires`-expression evaluate its expressions at run time?", "No — they're unevaluated operands; only their validity is checked at compile time.")]),

dict(title="constexpr, consteval, constinit, and if consteval", std="C++23", minutes=12, area="Compile-time programming",
features=[("`constexpr` variables and functions", "C++11 (relaxed C++14)"), ("`constexpr` virtual, try, dynamic allocation in constant evaluation", "C++20"), ("`consteval` (immediate functions)", "C++20"), ("`constinit`", "C++20"), ("`if consteval`", "C++23"), ("`std::is_constant_evaluated`", "C++20"), ("Static initialization order fiasco", "C++98")],
why="""
A DSP filter needs a 256-entry sine table. You can compute it at startup — or have the *compiler* compute
it so it's baked into the binary, costs zero time at run time, and fits in read-only flash on a
microcontroller. That's `constexpr`. Its siblings `consteval` and `constinit` give you stronger guarantees.
""",
body="""
## `constexpr`: *may* run at compile time

A `constexpr` function can be evaluated at compile time if its arguments are constants and its result is
needed as a constant; otherwise it runs normally. Since C++20, constexpr functions can use loops,
`std::vector`/`std::string` (as long as the memory is freed before evaluation ends), virtual calls, and
`try` blocks. UB during constant evaluation is a *compile error* — a free UB detector for your tests.

## `consteval`: *must* run at compile time

An immediate function. Every call must produce a constant — great for validating format strings, units,
or IDs at compile time.

## `constinit`: initialized at compile time, mutable afterwards

`constinit` asserts that a global/static variable has **static initialization** (no dynamic
initializer at startup). This kills the *static initialization order fiasco* — where one global's
constructor uses another global from a different .cpp file that hasn't been initialized yet.

{{ex}}

## `if consteval` (C++23)

Inside a `constexpr` function, choose a compile-time-friendly path vs. a fast run-time path (e.g. an
intrinsic or a lookup table that isn't constexpr). It replaces `if (std::is_constant_evaluated())`, which
had a famous trap: inside `if constexpr (std::is_constant_evaluated())` it's always true.

!!! tip "Pro tip: test with static_assert"
    If your parsing or math is `constexpr`, add `static_assert(parse("42") == 42);` — tests that run every
    time you compile, and that fail on UB.
""",
files={"": r'''
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <string_view>
#include <vector>

constexpr double sin_approx(double x) {           // Taylor series: constexpr-friendly
    double term = x, sum = x;
    for (int n = 1; n < 10; ++n) { term *= -x * x / ((2 * n) * (2 * n + 1)); sum += term; }
    return sum;
}

template <std::size_t N>
constexpr std::array<std::int16_t, N> make_sine_table() {
    std::array<std::int16_t, N> t{};
    constexpr double pi = 3.14159265358979323846;
    for (std::size_t i = 0; i < N; ++i) {
        double x = 2 * pi * static_cast<double>(i) / N;
        if (x > pi) x -= 2 * pi;                  // keep the series accurate
        t[i] = static_cast<std::int16_t>(sin_approx(x) * 32767);
    }
    return t;
}
constexpr auto sine = make_sine_table<256>();    // computed by the compiler
static_assert(sine[64] > 32700);                 // a compile-time test

constexpr int sum_squares(int n) {               // C++20: std::vector in constant evaluation
    std::vector<int> v(static_cast<std::size_t>(n));
    std::iota(v.begin(), v.end(), 1);
    int s = 0;
    for (int x : v) s += x * x;
    return s;
}
static_assert(sum_squares(3) == 14);

consteval std::uint32_t fourcc(std::string_view s) {   // must be compile time
    if (s.size() != 4) throw "fourcc needs exactly 4 chars";   // compile error if hit
    return std::uint32_t(s[0]) | std::uint32_t(s[1]) << 8 | std::uint32_t(s[2]) << 16 | std::uint32_t(s[3]) << 24;
}

constexpr double fast_sqrt(double x) {
    if consteval { double r = x; for (int i = 0; i < 30; ++i) r = 0.5 * (r + x / r); return r; }
    else { return std::sqrt(x); }                // run time: use the library
}

constinit int frame_counter = 0;                 // statically initialized; still mutable

int main() {
    std::cout << "sine[0]=" << sine[0] << " sine[64]=" << sine[64] << " sine[192]=" << sine[192] << '\n';
    std::cout << "sum_squares(10)=" << sum_squares(10) << '\n';
    constexpr auto riff = fourcc("RIFF");
    std::cout << std::hex << "RIFF=0x" << riff << std::dec << '\n';
    constexpr double s2 = fast_sqrt(2.0);
    volatile double two = 2.0;
    std::cout << s2 << ' ' << fast_sqrt(two) << '\n';
    ++frame_counter;
    std::cout << "frame_counter=" << frame_counter << '\n';
}
''', "_bad": {"expect": "fail", "std": "c++23", "code": r'''
// consteval rejects a non-constant use; UB in constant evaluation is a compile error
#include <string_view>
consteval int len4(std::string_view s) { if (s.size() != 4) throw "need 4"; return 4; }
constexpr int overflow() { int x = 2147483647; return x + 1; }
int main() {
    constexpr int a = len4("RIFFX");   // error: throw in constant evaluation
    constexpr int b = overflow();      // error: signed overflow is UB -> not a constant
    return a + b;
}
'''}},
takeaways=["`constexpr` functions may run at compile time; constant evaluation rejects UB.",
"`consteval` functions must run at compile time — great for validating literals.",
"`constinit` guarantees static initialization, avoiding the initialization order fiasco.",
"`if consteval` (C++23) picks a compile-time path vs. a run-time path."],
quiz=[("What's the difference between `constexpr` and `consteval` functions?", "`constexpr` functions *can* be evaluated at compile time; `consteval` functions *must* be (every call is a constant expression)."),
("Does `constinit` make a variable const?", "No — it only guarantees compile-time (static) initialization; the variable remains mutable."),
("What happens if a `constexpr` computation used in a `static_assert` overflows a signed int?", "Compile error: undefined behaviour isn't allowed in constant evaluation.")]),

dict(title="Lambdas in depth", std="C++23", minutes=11, area="Functional programming",
features=[("Lambda expressions, captures by value/reference", "C++11"), ("Init captures, `mutable`", "C++14"), ("Generic lambdas", "C++14"), ("`constexpr` lambdas", "C++17"), ("`[*this]` capture", "C++17"), ("Template lambdas `[]<typename T>`", "C++20"), ("Lambdas in unevaluated contexts, default-constructible stateless lambdas", "C++20"), ("`static operator()` lambdas", "C++23"), ("Immediately-invoked lambdas (IILE)", "—")],
why="""
Sorting tracks by duration, filtering sensor readings above a threshold, registering a callback for "new
frame ready" — all need a small function right where you use it. Lambdas are that. And they're not slow:
each lambda is a tiny class the compiler can inline completely.
""",
body="""
## Anatomy

```cpp
[captures](params) mutable -> ReturnType { body }
```

A lambda creates an object of a unique, unnamed class with an `operator()`. Captures become its members.

| Capture | Meaning |
|---|---|
| `[x]` | copy `x` |
| `[&x]` | reference to `x` |
| `[=]` / `[&]` | everything used, by copy / by reference |
| `[p = std::move(ptr)]` | init capture (C++14): move-only values, renaming |
| `[this]` / `[*this]` | the object by pointer / by copy (C++17) |

## The wrong way: dangling reference captures

```cpp
std::function<int()> make_counter() {
    int count = 0;
    return [&count] { return ++count; };   // count dies when make_counter returns: UB
}
```

Capturing by reference is fine for lambdas used *immediately* (e.g. passed to `std::sort`). For lambdas
that are *stored* (callbacks, threads), capture by value or init-capture.

{{ex}}

## Generic and template lambdas

`[](const auto& a, const auto& b)` is a generic lambda (a template `operator()`). C++20 template lambdas
`[]<typename T>(const std::vector<T>& v)` let you name the type.

## IILE: initialize a const with complex logic

```cpp
const auto config = [&] { Config c; /* many steps */ return c; }();
```

!!! tip "Pro tip"
    `mutable` lets a by-copy lambda modify its own copies. State lives in the lambda object, so copies of
    the lambda have *independent* state.
""",
files={"": r'''
#include <algorithm>
#include <functional>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

struct Track { std::string title; int seconds; };

class Player {
public:
    auto make_logger() const { return [*this] { std::cout << "player volume " << volume_ << '\n'; }; }  // copy of *this
    int volume_ = 7;
};

int main() {
    std::vector<Track> tracks{{"So What", 562}, {"Blue in Green", 337}, {"All Blues", 693}};

    std::ranges::sort(tracks, [](const Track& a, const Track& b) { return a.seconds < b.seconds; });
    for (const auto& t : tracks) std::cout << t.title << " (" << t.seconds << "s)\n";

    int threshold = 400;
    auto longer = std::ranges::count_if(tracks, [threshold](const Track& t) { return t.seconds > threshold; });
    std::cout << longer << " tracks longer than " << threshold << "s\n";

    auto counter = [n = 0]() mutable { return ++n; };   // init capture + mutable
    auto copy = counter;
    std::cout << counter() << counter() << ' ' << copy() << '\n';

    auto owned = std::make_unique<std::string>("owned buffer");
    auto task = [buf = std::move(owned)] { return buf->size(); };   // move-only capture
    std::cout << "task sees " << task() << " chars\n";

    auto add = [](const auto& a, const auto& b) { return a + b; };   // generic
    std::cout << add(1, 2) << ' ' << add(std::string{"a"}, std::string{"b"}) << '\n';

    auto first_or = []<typename T>(const std::vector<T>& v, T fallback) { return v.empty() ? fallback : v.front(); };
    std::cout << first_or(std::vector<int>{}, -1) << '\n';

    constexpr auto square = [](int x) { return x * x; };
    static_assert(square(5) == 25);

    auto cube = [](int x) static { return x * x * x; };   // C++23: no `this` needed
    std::cout << cube(3) << '\n';

    Player p;
    auto log = p.make_logger();
    p.volume_ = 11;
    log();                                                // still 7: captured a copy

    const std::string mode = [&] { return threshold > 300 ? std::string{"long"} : std::string{"short"}; }();
    std::cout << "mode=" << mode << '\n';
}
''', "std": "c++23"},
takeaways=["A lambda is an object of an unnamed class; captures are its members.",
"Capture by reference only for lambdas used before the captured variables die.",
"Init captures move in move-only state; `mutable` allows modifying copies.",
"Generic, template, constexpr and (C++23) static lambdas cover most callback needs."],
quiz=[("Why is `[&count]` dangerous in a returned lambda?", "The lambda outlives `count`, a local variable; calling it later reads a dangling reference (UB)."),
("Why did `copy()` print 1 while `counter` printed 1 then 2?", "`copy` was copied from `counter` before it was called, so it has its own independent `n`."),
("How do you capture a `std::unique_ptr` into a lambda?", "With an init capture: `[p = std::move(ptr)] { ... }`.")]),

dict(title="Callables: std::function, move_only_function, and type erasure", std="C++23", minutes=11, area="Functional programming",
features=[("`std::function`", "C++11"), ("`std::move_only_function`", "C++23"), ("`std::function_ref`", "C++26 (preview)"), ("`std::invoke`, `std::invoke_r`", "C++17/23"), ("`std::bind_front`, `std::bind_back`", "C++20/23"), ("Member function pointers", "C++98"), ("Type erasure (concept/model pattern)", "—")],
why="""
Lambdas each have a unique type. So how do you store *different* callbacks in one `std::vector`? Or keep a
callback as a class member without making the whole class a template? You need a type that can hold "any
callable with signature `void(int)`". That's `std::function` — and understanding how it works teaches you
**type erasure**, one of the most powerful designs in C++.
""",
body="""
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

{{ex}}

## How type erasure works

Inside, `std::function` holds a pointer to an abstract "concept" interface, and a templated "model" that
implements it for the concrete callable type. The template is only visible at construction; afterwards the
type is "erased" behind a virtual call. The example builds a tiny `AnyDrawable` the same way — runtime
polymorphism *without* requiring your types to inherit from anything.

!!! warning "Costs"
    Calling through `std::function` is an indirect call that's hard to inline, and storing a large lambda
    may allocate. Fine for event callbacks; avoid in per-sample DSP loops.
""",
files={"": r'''
#include <functional>
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

struct Track { std::string title; int seconds; int duration_min() const { return seconds / 60; } };

class EventBus {                                     // stored callbacks
public:
    void subscribe(std::function<void(const std::string&)> cb) { subs_.push_back(std::move(cb)); }
    void publish(const std::string& e) const { for (const auto& s : subs_) s(e); }
private:
    std::vector<std::function<void(const std::string&)>> subs_;
};

// Hand-written type erasure: anything with a draw() member
class AnyDrawable {
public:
    template <typename T>
    AnyDrawable(T obj) : self_{std::make_unique<Model<T>>(std::move(obj))} {}
    void draw() const { self_->draw(); }
private:
    struct Concept { virtual ~Concept() = default; virtual void draw() const = 0; };
    template <typename T>
    struct Model final : Concept {
        explicit Model(T o) : obj{std::move(o)} {}
        void draw() const override { obj.draw(); }
        T obj;
    };
    std::unique_ptr<Concept> self_;
};
struct Circle { void draw() const { std::cout << "  circle\n"; } };
struct Label { std::string text; void draw() const { std::cout << "  label: " << text << '\n'; } };

int main() {
    EventBus bus;
    int received = 0;
    bus.subscribe([&received](const std::string& e) { ++received; std::cout << "ui got " << e << '\n'; });
    bus.subscribe([](const std::string& e) { std::cout << "logger got " << e << '\n'; });
    bus.publish("track-changed");

    std::move_only_function<int()> job = [p = std::make_unique<int>(41)] { return *p + 1; };
    std::cout << "move_only_function: " << job() << '\n';

    Track t{"So What", 562};
    std::cout << std::invoke(&Track::title, t) << ' ' << std::invoke(&Track::duration_min, t) << "min\n";

    auto add = [](int a, int b) { return a + b; };
    auto add10 = std::bind_front(add, 10);
    std::cout << add10(5) << ' ' << received << '\n';

    std::vector<AnyDrawable> scene{Circle{}, Label{"hello"}};
    for (const auto& d : scene) d.draw();
}
''', "std": "c++23", "maybe_unsupported": True},
takeaways=["`std::function` stores any copyable callable with a given signature; `std::move_only_function` (C++23) allows move-only ones.",
"`std::function_ref` (C++26) is a non-owning view for parameters.",
"`std::invoke` calls functions, lambdas and member pointers uniformly.",
"Type erasure = abstract concept + templated model, hidden behind a value-semantic wrapper."],
quiz=[("Why can't `std::function` hold a lambda that captures a `std::unique_ptr`?", "`std::function` requires the callable to be copyable; such a lambda is move-only. Use `std::move_only_function`."),
("When should a function take a template `F&&` instead of `std::function`?", "When it calls the callable immediately and doesn't store it — the template has no type-erasure overhead and inlines."),
("In type erasure, where does the concrete type survive?", "Only inside the templated `Model<T>`, created in the wrapper's constructor template; the wrapper itself sees only the abstract `Concept`.")]),

dict(title="CRTP, deducing this, and a taste of metaprogramming", std="C++23", minutes=11, area="Templates & generic programming",
features=[("CRTP (curiously recurring template pattern)", "C++98"), ("Explicit object parameter (deducing `this`)", "C++23"), ("Static polymorphism vs dynamic polymorphism", "—"), ("Template metaprogramming basics (recursive templates, type lists)", "C++11"), ("`std::integer_sequence` / `std::index_sequence`", "C++14"), ("Expression templates (overview)", "—")],
why="""
Virtual functions cost an indirect call and block inlining. If you know all types at compile time, you can
get polymorphism with *zero* runtime cost: the base class template knows the derived type and calls it
directly. That's CRTP — and C++23's "deducing this" makes much of it simpler. This lesson is
intermediate-to-advanced; it's fine to skim the metaprogramming part on a first pass.
""",
body="""
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

{{ex}}

## Metaprogramming in one breath

Templates are Turing complete; you can compute with types. Modern code mostly uses `constexpr` for values
and concepts for constraints, but `std::index_sequence` (compile-time list of indices) is still everyday
useful, e.g. for iterating over a tuple — see the example's `print_tuple`. **Expression templates** (used by
Eigen and similar libraries) build an expression tree as types so that `a + b + c` on vectors runs as one
loop with no temporaries — a topic for further reading.
""",
files={"": r'''
#include <cstddef>
#include <iostream>
#include <string>
#include <tuple>
#include <utility>

template <typename Derived>
struct Shape {                                         // CRTP static interface
    double area() const { return static_cast<const Derived&>(*this).area_impl(); }
};
struct Square : Shape<Square> { double s; explicit Square(double x) : s{x} {} double area_impl() const { return s * s; } };
struct Circle : Shape<Circle> { double r; explicit Circle(double x) : r{x} {} double area_impl() const { return 3.14159 * r * r; } };

template <typename T>
double total_area(const Shape<T>& a, const Shape<T>& b) { return a.area() + b.area(); }

template <typename Derived>
struct InstanceCounter {                               // CRTP mixin: per-class counter
    inline static int count = 0;
    InstanceCounter() { ++count; }
};
struct Widget : InstanceCounter<Widget> {};
struct Gadget : InstanceCounter<Gadget> {};

struct Buffer {
    std::string data = "abc";
    template <typename Self>
    auto& get(this Self& self) { return self.data; }    // deducing this: const and non-const in one
};

struct Base {
    void describe(this const auto& self) { std::cout << "I am " << self.name() << '\n'; }
};
struct Mic : Base { std::string name() const { return "a microphone"; } };

template <typename Tuple, std::size_t... I>
void print_tuple_impl(const Tuple& t, std::index_sequence<I...>) {
    ((std::cout << (I == 0 ? "" : ", ") << std::get<I>(t)), ...);
}
template <typename... Ts>
void print_tuple(const std::tuple<Ts...>& t) {
    std::cout << '(';
    print_tuple_impl(t, std::index_sequence_for<Ts...>{});
    std::cout << ")\n";
}

int main() {
    std::cout << total_area(Square{2}, Square{3}) << ' ' << Circle{1}.area() << '\n';
    Widget w1, w2; Gadget g1;
    std::cout << "widgets=" << Widget::count << " gadgets=" << Gadget::count << '\n';

    Buffer b;
    b.get() += "d";
    const Buffer& cb = b;
    std::cout << cb.get() << '\n';                     // const version, same function

    Mic{}.describe();

    auto fib = [](this auto self, int n) -> int { return n < 2 ? n : self(n - 1) + self(n - 2); };  // recursive lambda
    std::cout << "fib(10)=" << fib(10) << '\n';
    print_tuple(std::tuple{1, 2.5, std::string{"three"}});
    (void)w1; (void)w2; (void)g1;
}
''', "std": "c++23"},
takeaways=["CRTP gives compile-time polymorphism and mixins with no virtual calls.",
"Deducing `this` (C++23) deduces the object's type: one function for const/non-const, recursive lambdas, simpler mixins.",
"Use `std::index_sequence` to expand over tuple elements at compile time.",
"Pick dynamic polymorphism for open, runtime sets of types; static for known types in hot paths."],
quiz=[("What's the main limitation of CRTP vs virtual functions?", "No common base type: `Shape<Square>` and `Shape<Circle>` are unrelated, so you can't store them in one container and choose at run time."),
("What does `template <typename Self> auto& get(this Self& self)` replace?", "A pair of overloads `T& get()` and `const T& get() const` (and possibly && versions)."),
("Why does `InstanceCounter<Widget>::count` differ from `InstanceCounter<Gadget>::count`?", "They're different class template instantiations, each with its own static member.")]),
],
assignment=dict(title="A typed event dispatcher", task="""
Build `Dispatcher` that lets callers subscribe handlers for different event *types*:

```cpp
d.on<KeyPressed>([](const KeyPressed& e) { ... });
d.emit(KeyPressed{'a'});
```

Requirements: constrain events with a concept `Event` (must be copyable and have a static `name`),
store handlers type-erased in a `std::unordered_map<std::type_index, std::vector<std::function<void(const void*)>>>`,
and print how many handlers ran per emit.
""", solution=r'''
#include <concepts>
#include <functional>
#include <iostream>
#include <string_view>
#include <typeindex>
#include <unordered_map>
#include <vector>

template <typename E>
concept Event = std::copyable<E> && requires { { E::name } -> std::convertible_to<std::string_view>; };

class Dispatcher {
public:
    template <Event E, std::invocable<const E&> F>
    void on(F handler) {
        handlers_[typeid(E)].push_back([h = std::move(handler)](const void* p) { h(*static_cast<const E*>(p)); });
    }
    template <Event E>
    void emit(const E& e) const {
        auto it = handlers_.find(typeid(E));
        const std::size_t n = it == handlers_.end() ? 0 : it->second.size();
        if (n) for (const auto& h : it->second) h(&e);
        std::cout << "  [" << E::name << ": " << n << " handler(s)]\n";
    }
private:
    std::unordered_map<std::type_index, std::vector<std::function<void(const void*)>>> handlers_;
};

struct KeyPressed { static constexpr std::string_view name = "KeyPressed"; char key; };
struct Resized { static constexpr std::string_view name = "Resized"; int w, h; };

int main() {
    Dispatcher d;
    int keys = 0;
    d.on<KeyPressed>([&keys](const KeyPressed& e) { ++keys; std::cout << "key " << e.key << '\n'; });
    d.on<KeyPressed>([](const KeyPressed&) { std::cout << "beep\n"; });
    d.emit(KeyPressed{'a'});
    d.emit(Resized{800, 600});
    d.on<Resized>([](const Resized& r) { std::cout << "resized to " << r.w << 'x' << r.h << '\n'; });
    d.emit(Resized{1024, 768});
    std::cout << "keys=" << keys << '\n';
}
'''))
