WEEK = dict(num=5, title="Value semantics: copy, move, and value categories", intro="""
This is the week many people describe as "the moment C++ finally made sense". We'll look at what it
means to *copy* an object, then at **move semantics** — the C++11 feature that lets you transfer resources
instead of duplicating them — and the idea underneath it: *value categories*.

Honest warning: value categories are one of the most confusing topics in C++. We'll go slowly, with lots of
printed output so you can *see* which constructor runs. If it doesn't fully click this week, that's
completely normal; it'll click after you use it.
""", lessons=[
dict(title="Copy semantics and the Rule of Three", std="C++20", minutes=11, area="OOP: value semantics",
features=[("Copy constructor, copy assignment operator", "C++98"), ("Shallow vs deep copy", "—"), ("Rule of Three", "C++98"), ("Copy-and-swap idiom, self-assignment", "C++98"), ("Implicitly generated special member functions", "C++11")],
why="""
Write a class that owns a heap buffer with a raw pointer, copy it once, and your program will crash at exit
with a double free. Why? The compiler-generated copy just copies the *pointer*, so two objects think they own
the same buffer. Understanding exactly what "copy" means for your class is the foundation for everything
this week.
""",
body="""
## The six special member functions

For every class, the compiler can generate: default constructor, destructor, copy constructor, copy
assignment, move constructor, move assignment. The generated copy operations copy **each member**.
For an `int` or `std::string` member, that's perfect. For a raw owning pointer, it's a disaster.

## The wrong way: shallow copy of an owning pointer

```cpp
class Buffer {
    float* data_; std::size_t n_;
public:
    explicit Buffer(std::size_t n) : data_{new float[n]{}}, n_{n} {}
    ~Buffer() { delete[] data_; }
    // no copy operations written: compiler copies the pointer
};
Buffer a{1024};
Buffer b = a;    // b.data_ == a.data_  -> both destructors delete[] it -> double free (UB)
```

## The Rule of Three

> If a class needs a user-written destructor, copy constructor, or copy assignment operator, it almost
> certainly needs all three.

Because a custom destructor means "I manage a resource", and then copying must decide what happens to that
resource: **deep copy** (duplicate it), **forbid copying** (`= delete`), or **share it** (reference count).

## A correct deep copy, with copy-and-swap

{{ex}}

The **copy-and-swap** idiom for assignment: take the parameter *by value* (that makes the copy), then swap
our contents with it. The old contents get destroyed with the parameter. It's automatically safe for
self-assignment (`a = a`) and gives the strong exception guarantee (Week 9): if the copy throws, `*this`
is untouched. It's not always the fastest, but it's very hard to get wrong.

!!! tip "Pro tip: the best Rule of Three is no rule at all"
    If `Buffer` held a `std::vector<float>` instead of a raw pointer, you'd write *none* of these functions
    and copying would just work. That's the Rule of Zero, coming in Lesson 5.3.
""",
files={"": r'''
#include <algorithm>
#include <cstddef>
#include <iostream>
#include <utility>

class Buffer {
public:
    explicit Buffer(std::size_t n) : data_{new float[n]{}}, n_{n} { std::cout << "  ctor(" << n << ")\n"; }
    ~Buffer() { delete[] data_; }

    Buffer(const Buffer& other) : data_{new float[other.n_]}, n_{other.n_} {   // deep copy
        std::copy(other.data_, other.data_ + n_, data_);
        std::cout << "  copy ctor\n";
    }
    Buffer& operator=(Buffer other) {          // copy-and-swap: `other` is already a copy
        std::cout << "  copy assign (swap)\n";
        swap(*this, other);
        return *this;
    }                                          // old contents die with `other`
    friend void swap(Buffer& a, Buffer& b) noexcept {
        using std::swap;
        swap(a.data_, b.data_);
        swap(a.n_, b.n_);
    }

    float& operator[](std::size_t i) { return data_[i]; }
    std::size_t size() const { return n_; }

private:
    float* data_;
    std::size_t n_;
};

int main() {
    Buffer a{4};
    a[0] = 1.5f;
    Buffer b = a;            // copy constructor
    b[0] = 9.0f;             // independent copy
    std::cout << "a[0]=" << a[0] << " b[0]=" << b[0] << '\n';

    Buffer c{2};
    c = a;                   // copy assignment
    Buffer& alias = c;
    c = alias;               // self-assignment (through an alias) is safe
    std::cout << "c.size()=" << c.size() << " c[0]=" << c[0] << '\n';
}
'''},
takeaways=["Compiler-generated copies copy each member; for raw owning pointers that means double frees.",
"Rule of Three: a custom destructor, copy ctor or copy assignment usually means you need all three.",
"Copy-and-swap gives safe, exception-safe assignment with little code.",
"Better still: hold resources in members that already copy correctly (Rule of Zero)."],
quiz=[("What does the implicitly generated copy constructor do?", "Copy-constructs each base and member in declaration order (memberwise copy)."),
("Why is copy-and-swap safe for self-assignment?", "The parameter is a full copy made before anything in `*this` changes, so swapping with it is fine even if the source was `*this`."),
("Your class has a `std::FILE*` it closes in the destructor. What are your options for copying?", "Delete copying (most common), implement a deep copy (open another handle — rarely meaningful), or share ownership with reference counting (e.g. `std::shared_ptr` with a deleter).")]),

dict(title="Value categories: lvalues, prvalues, xvalues", std="C++20", minutes=12, area="OOP: value semantics",
features=[("Value categories: lvalue, prvalue, xvalue (glvalue, rvalue)", "C++11"), ("Rvalue references `T&&`", "C++11"), ("Overloading on `&` vs `&&` parameters", "C++11"), ("Temporaries and temporary materialization", "C++17"), ("`decltype((x))` reveals value category", "C++11")],
why="""
To make moves work, the compiler needs to know one thing about every expression: *is this an object that
someone still cares about, or one that's about to disappear?* If it's about to disappear, it's safe to steal
its insides. That's what value categories are — and despite the scary names, the intuition is simple.
""",
body="""
## The intuition: "has a name / identity" vs "about to die"

- An **lvalue** is an expression that refers to an object with identity that will still exist after the
  expression: a named variable `x`, `*p`, `v[0]`, a function returning `T&`. You can take its address.
- A **prvalue** ("pure rvalue") is a value with no identity yet: `42`, `a + b`, `std::string{"hi"}`,
  a function returning `T` by value. It's a recipe for creating an object.
- An **xvalue** ("expiring value") is an object that *has* identity but which we've declared we're done
  with: `std::move(x)`, or a function returning `T&&`.

Grouping them: **rvalues** = prvalues + xvalues ("can be moved from"); **glvalues** = lvalues + xvalues
("has identity").

```mermaid
flowchart TD
  E[expression] --> G[glvalue: has identity]
  E --> R[rvalue: can be moved from]
  G --> L[lvalue]
  G --> X[xvalue]
  R --> X
  R --> P[prvalue]
```

## Rvalue references: `T&&`

A `T&&` parameter binds **only to rvalues**. So you can overload a function: one version for lvalues
(`const T&`: "I'll copy if needed") and one for rvalues (`T&&`: "you can steal from this").

{{ex}}

Read that output carefully, especially the last line. Inside `take(std::string&& s)`, the parameter
`s` **is an lvalue**! It has a name, so it's not about to disappear inside the function. That's why,
to pass it on as an rvalue, you'd have to say `std::move(s)` again. This is the #1 confusion about
rvalue references: *the type is "rvalue reference", the expression `s` is an lvalue.*

## Seeing categories with `decltype`

`decltype((expr))` (double parentheses!) gives `T&` for lvalues, `T&&` for xvalues and `T` for prvalues.
The example uses this to print categories — a nice trick for experiments in Compiler Explorer.

## C++17: guaranteed copy elision and temporary materialization

Since C++17 a prvalue isn't an object until it needs to be: `T x = T{};` constructs *directly* into `x` —
no temporary, no move. The prvalue is only "materialized" into a temporary (becoming an xvalue) when it
must be, e.g. when binding to a reference. We'll use this in Lesson 5.4.

!!! note "Don't memorize the taxonomy"
    You need two working rules: (1) a named thing is an lvalue, even if its type is `T&&`; (2)
    `std::move(x)` turns `x` into an rvalue so a move can happen.
""",
files={"": r'''
#include <iostream>
#include <string>
#include <type_traits>
#include <utility>

template <class T> constexpr const char* category() {
    if constexpr (std::is_lvalue_reference_v<T>) return "lvalue";
    else if constexpr (std::is_rvalue_reference_v<T>) return "xvalue";
    else return "prvalue";
}
#define CATEGORY(...) category<decltype((__VA_ARGS__))>()

void take(const std::string& s) { std::cout << "  take(const&)  [copy if needed]: " << s << '\n'; }
void take(std::string&& s) {
    std::cout << "  take(&&)      [may steal]: " << s << '\n';
    std::cout << "    inside, `s` is an " << CATEGORY(s) << '\n';
}

std::string make() { return "made"; }

int main() {
    std::string name = "named";
    int x = 1;
    std::cout << "x: " << CATEGORY(x) << ", 42: " << CATEGORY(42) << ", x + 1: " << CATEGORY(x + 1)
              << ", std::move(x): " << CATEGORY(std::move(x)) << ", make(): " << CATEGORY(make()) << '\n';

    take(name);                 // lvalue  -> const&
    take(make());               // prvalue -> &&
    take(std::string{"temp"});  // prvalue -> &&
    take(std::move(name));      // xvalue  -> &&
}
'''},
takeaways=["lvalue: has identity and persists; prvalue: a value with no identity yet; xvalue: an object we've marked as expiring.",
"`T&&` parameters bind only to rvalues; overload on `const T&` / `T&&` to copy or steal.",
"A named rvalue reference is an lvalue expression — use `std::move` again to pass it on.",
"`decltype((e))` reveals the value category; C++17 prvalues materialize only when needed."],
quiz=[("Classify: `v[0]` (vector<int> v), `v.size()`, `std::move(v)`, `\"hello\"`.", "`v[0]` lvalue (returns `int&`); `v.size()` prvalue; `std::move(v)` xvalue; a string literal is an lvalue (an array object with static storage)."),
("Inside `void f(Widget&& w)`, which overload does `g(w)` call: `g(const Widget&)` or `g(Widget&&)`?", "`g(const Widget&)`. `w` is a named variable, hence an lvalue. To call the `&&` overload write `g(std::move(w))`."),
("What's the difference between `decltype(x)` and `decltype((x))` for `int x`?", "`decltype(x)` is the declared type `int`; `decltype((x))` treats `(x)` as an lvalue expression and gives `int&`.")]),

dict(title="Move semantics, std::move, and the Rules of Five and Zero", std="C++20", minutes=12, area="OOP: value semantics",
features=[("Move constructor, move assignment", "C++11"), ("`std::move` (it's just a cast)", "C++11"), ("Moved-from state: valid but unspecified", "C++11"), ("`noexcept` moves and `std::vector` reallocation", "C++11"), ("Rule of Five, Rule of Zero", "C++11"), ("Move-only types", "C++11")],
why="""
Returning a 4K video frame from a function, or pushing a big buffer into a `std::vector`, would copy
megabytes in C++98. With move semantics, it copies three pointers. That's not a micro-optimization — it
changes how you design APIs: you can pass and return big objects *by value* again, which is simpler and
safer. Let's write a move constructor and watch the difference.
""",
body="""
## The idea: steal, then leave the source in a valid state

A **move constructor** `T(T&& other) noexcept` takes the resources out of `other` (pointers, handles) and
leaves `other` *valid but unspecified* — typically empty. Destroying or reassigning a moved-from object
must still work.

{{ex}}

Look at the counts: the moves cost nothing like the copy.

## `std::move` doesn't move anything

`std::move(x)` is just a cast to `T&&` — it says "I'm done with `x`, you may steal from it". The actual
moving happens in the move constructor/assignment that then gets selected. Two consequences:

- `std::move` on a `const` object silently **copies** (a `const T&&` can't bind to `T&&`, so overload
  resolution falls back to the copy constructor).
- After `std::move(x)`, don't use `x` except to assign to it or destroy it.

## Why `noexcept` matters

When `std::vector` grows, it moves elements to the new storage — **only if the move constructor is
`noexcept`**. Otherwise it copies, so that if a copy throws it can leave the old storage intact (the strong
guarantee). Forget `noexcept` on your move constructor and vector growth silently becomes copies. The
example shows both.

## Rule of Five and Rule of Zero

- **Rule of Five**: if you write any of destructor / copy ctor / copy assign / move ctor / move assign,
  think about all five. (Declaring a destructor or copy operation suppresses the implicit moves!)
- **Rule of Zero**: better — design classes so they need *none*. Hold resources in members that manage
  themselves (`std::vector`, `std::string`, `std::unique_ptr`). Then the compiler-generated operations are
  correct and as efficient as possible.

```cpp
struct Track {                     // Rule of Zero: no special members written
    std::string title;
    std::vector<float> samples;
    std::unique_ptr<Decoder> dec;  // makes Track move-only, automatically
};
```

!!! warning "Common pitfall: `return std::move(local);`"
    Don't. It *prevents* copy elision (next lesson), and `return local;` already moves automatically.
    Compilers warn with `-Wpessimizing-move`.
""",
files={"": r'''
#include <cstring>
#include <iostream>
#include <utility>
#include <vector>

struct Counts { int copies = 0, moves = 0; } counts;

class Frame {
public:
    explicit Frame(std::size_t n) : n_{n}, px_{new unsigned char[n]{}} {}
    ~Frame() { delete[] px_; }
    Frame(const Frame& o) : n_{o.n_}, px_{new unsigned char[o.n_]} {
        std::memcpy(px_, o.px_, n_);
        ++counts.copies;
    }
    Frame(Frame&& o) noexcept : n_{std::exchange(o.n_, 0)}, px_{std::exchange(o.px_, nullptr)} {
        ++counts.moves;                          // steal; leave o empty but valid
    }
    Frame& operator=(Frame o) noexcept {         // handles both copy and move assignment
        std::swap(n_, o.n_);
        std::swap(px_, o.px_);
        return *this;
    }
    std::size_t size() const { return n_; }
private:
    std::size_t n_;
    unsigned char* px_;
};

struct NoexceptLess {               // move constructor NOT noexcept
    NoexceptLess() = default;
    NoexceptLess(const NoexceptLess&) { ++counts.copies; }
    NoexceptLess(NoexceptLess&&) { ++counts.moves; }
};

int main() {
    Frame a{3840 * 2160 * 4};
    Frame b = a;                 // copy: allocates and memcpy's ~33 MB
    Frame c = std::move(a);      // move: steals the pointer
    std::cout << "copies=" << counts.copies << " moves=" << counts.moves
              << " a.size()=" << a.size() << " c.size()=" << c.size() << '\n';

    counts = {};
    std::vector<Frame> v;
    for (int i = 0; i < 5; ++i) v.push_back(Frame{16});   // growth moves (noexcept)
    std::cout << "vector<Frame>: copies=" << counts.copies << " moves=" << counts.moves << '\n';

    counts = {};
    std::vector<NoexceptLess> w;
    for (int i = 0; i < 5; ++i) w.emplace_back();          // growth must COPY existing elements
    std::cout << "vector<NoexceptLess>: copies=" << counts.copies << " moves=" << counts.moves << '\n';

    const Frame k{8};
    Frame m = std::move(k);      // const: this silently copies!
    std::cout << "after moving a const: copies=" << counts.copies + 0 << " (one more copy)\n";
    (void)m;
}
'''},
takeaways=["A move constructor steals resources and leaves the source valid but unspecified (usually empty).",
"`std::move` is only a cast; moving a `const` object copies.",
"Mark move operations `noexcept`, or `std::vector` will copy on reallocation.",
"Prefer the Rule of Zero; otherwise follow the Rule of Five.",
"Don't write `return std::move(local);`."],
quiz=[("What does `std::move` actually do?", "`static_cast<T&&>` — it converts its argument to an xvalue so move overloads can be selected. It performs no moving itself."),
("Why might `std::vector<T>` copy elements during `push_back` even though `T` has a move constructor?", "If the move constructor isn't `noexcept` (and T is copyable), vector uses copies to keep the strong exception guarantee on reallocation (`std::move_if_noexcept`)."),
("Your class declares only a destructor. Does it get an implicit move constructor?", "No. A user-declared destructor suppresses the implicit move operations; moves fall back to (deprecated) implicit copies. Either `= default` the moves or follow the Rule of Zero."),
("Is it OK to call `v.size()` on a moved-from `std::vector`?", "Yes — it's in a valid but unspecified state, so calling functions without preconditions is fine (in practice it's empty). Calling `v[0]` would not be OK without checking.")]),

dict(title="Copy elision, RVO, and returning by value", std="C++20", minutes=9, area="OOP: value semantics",
features=[("Guaranteed copy elision for prvalues", "C++17"), ("Named return value optimization (NRVO)", "C++98"), ("Implicit move on return", "C++20"), ("Sink parameters: pass by value and move", "C++11")],
why="""
Should a function that builds a big vector return it, or take an output parameter `void build(std::vector<int>& out)`?
Old advice said "output parameter, to avoid the copy". Modern C++ says: just return it. Let's see why the
compiler makes that free — and the two simple rules for writing parameters that take ownership.
""",
body="""
## Guaranteed elision (C++17)

When you return a prvalue — `return Widget{args};` — C++17 *guarantees* the object is constructed
directly in the caller's storage. No copy, no move; the type doesn't even need to be copyable or movable.

## NRVO: named return value optimization

When you return a *named local*, `Widget w; ...; return w;`, the compiler is *allowed* (not required) to
construct `w` directly in the caller's storage. GCC and Clang do this whenever there's a single named
object returned on all paths. If it can't, **the return still moves** automatically (C++11, broadened in
C++20), never copies, as long as the type is movable.

{{ex}}

Count the "move" lines: zero for the two common patterns. The function returning one of two different
locals can't use NRVO, so it moves.

## Sink parameters: take by value, then move

If a function will *store* its argument (a constructor storing a name, `push_back`-like functions), take it
**by value** and `std::move` it into place:

```cpp
class Track {
    std::string title_;
public:
    explicit Track(std::string title) : title_{std::move(title)} {}
};
Track a{some_string};          // one copy (into the parameter) + one cheap move
Track b{"literal"};            // constructs the parameter directly + one cheap move
Track c{std::move(s)};         // two cheap moves, no copy
```

One function handles lvalues and rvalues nearly optimally. (The alternative — overloading on `const&` and
`&&` — saves a move but doubles the code.)

!!! tip "Rules you can apply without thinking"
    1. Return by value. Don't `std::move` the return expression.
    2. Read-only parameter → `const T&` (or by value for cheap types / `string_view` / `span`).
    3. Parameter you'll store → by value + `std::move`.
""",
files={"": r'''
#include <iostream>
#include <string>
#include <utility>

struct Loud {
    std::string tag;
    explicit Loud(std::string t) : tag{std::move(t)} { std::cout << "  construct " << tag << '\n'; }
    Loud(const Loud& o) : tag{o.tag} { std::cout << "  COPY " << tag << '\n'; }
    Loud(Loud&& o) noexcept : tag{std::move(o.tag)} { std::cout << "  move " << tag << '\n'; }
};

Loud make_prvalue() { return Loud{"prvalue"}; }          // guaranteed elision (C++17)
Loud make_named() { Loud w{"named"}; w.tag += "!"; return w; }   // NRVO in practice
Loud make_either(bool b) {
    Loud x{"x"}, y{"y"};
    if (b) return x;     // two candidates: no NRVO, but implicit move (never a copy)
    return y;
}

class Holder {
public:
    explicit Holder(Loud l) : l_{std::move(l)} {}   // sink parameter
private:
    Loud l_;
};

int main() {
    std::cout << "prvalue:\n";  Loud a = make_prvalue();
    std::cout << "named:\n";    Loud b = make_named();
    std::cout << "either:\n";   Loud c = make_either(true);
    std::cout << "sink from lvalue:\n";
    Holder h1{a};                    // copy into parameter, then move
    std::cout << "sink from rvalue:\n";
    Holder h2{std::move(b)};         // move into parameter, then move
    (void)c; (void)h1; (void)h2;
}
'''},
takeaways=["Returning a prvalue is guaranteed copy-free since C++17.",
"Returning a named local uses NRVO or, failing that, an implicit move — never write `return std::move(x)`.",
"Return results by value instead of using output parameters.",
"Sink parameters: take by value and `std::move` into the member."],
quiz=[("Can a function return a non-copyable, non-movable type by value in C++17?", "Yes, if it returns a prvalue (`return T{...};`), thanks to guaranteed copy elision."),
("Why can't the compiler apply NRVO in `if (b) return x; return y;`?", "There are two different named objects that might be returned, so neither can be constructed in the caller's storage in advance. The return falls back to an implicit move."),
("What's the cost of `Track t{name};` with a by-value sink constructor, where `name` is an lvalue string?", "One copy (into the parameter) plus one move (into the member).")]),

dict(title="Aggregates, designated initializers, structured bindings, user-defined literals", std="C++20", minutes=11, area="OOP: value semantics",
features=[("Aggregates and aggregate initialization", "C++98"), ("Designated initializers", "C++20"), ("Aggregate init with parentheses", "C++20"), ("Structured bindings", "C++17"), ("Structured bindings for your own types (tuple protocol)", "C++17"), ("User-defined literals", "C++11"), ("Standard literals: `s`, `sv`, `ms`, `i`", "C++14")],
why="""
Not every type needs constructors and private members. A lot of real code is just *data*: a config, a
point, a parsed header. C++ has a lightweight path for those types — aggregates — and C++17/20 made them
really pleasant to use: name the fields when creating them, unpack them by name when reading them. Let's
look at the modern toolbox for "plain data".
""",
body="""
## Aggregates

An **aggregate** is (roughly) an array or a class with no user-declared constructors, no private/protected
non-static data members, no virtual functions, and no virtual/private bases. You initialize it with braces
listing the members in order:

```cpp
struct Rgb { std::uint8_t r, g, b; };
Rgb red{255, 0, 0};
```

## Designated initializers (C++20)

Naming the members makes the call site self-documenting:

```cpp
EncoderConfig cfg{.bitrate = 128'000, .vbr = true};   // others get their default member initializers
```

Rules (stricter than C): designators must appear in **declaration order**, and you can't mix designated
and positional elements. C++20 also allows aggregate init with parentheses, `Rgb red(255, 0, 0);`, which
helps generic code like `std::make_unique<Rgb>(255, 0, 0)`.

## Structured bindings (C++17)

The reverse: unpack an aggregate, `std::pair`, `std::tuple` or array into named variables:

```cpp
for (const auto& [name, rate] : rates) ...       // map iteration, finally readable
auto [it, inserted] = set.insert(42);
```

The names are aliases into a hidden object, so `auto&` binds them by reference to the original. Your own
non-aggregate types can opt in by implementing the *tuple protocol* (`std::tuple_size`,
`std::tuple_element`, `get<I>`) — shown in the example.

## User-defined literals (C++11)

You've used standard ones: `"abc"s` (string), `"abc"sv`, `100ms` (chrono), `2.0i` (complex). You can
define your own with `operator""_suffix`; user suffixes must start with an underscore:

```cpp
constexpr Hertz operator""_kHz(unsigned long long v) { return Hertz{v * 1000}; }
auto rate = 48_kHz;
```

They're great for units: `48_kHz` can't be mixed up with `48`.

{{ex}}

!!! warning "Common pitfall: adding a constructor removes aggregate-ness"
    The moment you add *any* user-declared constructor (even `= default` since C++20), a struct stops being
    an aggregate and designated initializers stop compiling. Use default member initializers instead.
""",
files={"": r'''
#include <chrono>
#include <cstdint>
#include <iostream>
#include <map>
#include <string>
#include <tuple>

struct EncoderConfig {
    std::string codec = "aac";
    int bitrate = 96'000;
    int channels = 2;
    bool vbr = false;
};

struct Hertz { unsigned long long value; };
constexpr Hertz operator""_kHz(unsigned long long v) { return Hertz{v * 1000}; }

class Span2 {                               // a non-aggregate that supports structured bindings
public:
    Span2(int b, int e) : b_{b}, e_{e} {}
    template <std::size_t I> int get() const { if constexpr (I == 0) return b_; else return e_; }
private:
    int b_, e_;
};
template <> struct std::tuple_size<Span2> : std::integral_constant<std::size_t, 2> {};
template <std::size_t I> struct std::tuple_element<I, Span2> { using type = int; };

int main() {
    EncoderConfig cfg{.bitrate = 128'000, .vbr = true};
    std::cout << cfg.codec << ' ' << cfg.bitrate << ' ' << cfg.channels << ' ' << cfg.vbr << '\n';

    struct Rgb { std::uint8_t r, g, b; };
    Rgb teal(0, 128, 128);                   // C++20 parenthesized aggregate init
    auto [r, g, b] = teal;
    std::cout << int{r} << ',' << int{g} << ',' << int{b} << '\n';

    std::map<std::string, int> rates{{"cd", 44'100}, {"dvd", 48'000}};
    for (const auto& [name, rate] : rates) std::cout << name << '=' << rate << ' ';
    std::cout << '\n';

    if (auto [it, inserted] = rates.insert({"cd", 1}); !inserted)
        std::cout << "already had " << it->first << '\n';

    auto [begin, end] = Span2{3, 9};
    std::cout << "span " << begin << ".." << end << '\n';

    using namespace std::chrono_literals;
    auto rate = 48_kHz;
    auto frame = 20ms;
    std::cout << rate.value << " Hz, " << frame.count() << " ms, samples/frame = "
              << rate.value * static_cast<unsigned long long>(frame.count()) / 1000 << '\n';
}
'''},
takeaways=["Aggregates are plain data types initialized member-wise with braces.",
"C++20 designated initializers name fields at the call site (in declaration order).",
"Structured bindings unpack pairs, tuples, arrays, aggregates — and your types via the tuple protocol.",
"User-defined literals (`48_kHz`) make units explicit."],
quiz=[("Does `struct P { int x, y; }; P p{.y = 1, .x = 2};` compile in C++20?", "No — designators must appear in declaration order (`.x` before `.y`)."),
("In `for (auto& [k, v] : m)` over a `std::map`, can you modify `k`?", "No: map elements are `std::pair<const Key, T>`, so `k` refers to a const key. You can modify `v`."),
("Why must user-defined literal suffixes start with `_`?", "Suffixes without an underscore are reserved for the standard library (like `s`, `ms`, `sv`).")]),
],
assignment=dict(title="A move-aware audio clip", task="""
Build `class Clip` that owns samples (`std::vector<float>`), a name (`std::string`) and an id.

1. Follow the Rule of Zero for storage — but add *instrumentation*: a static counter of copies and moves
   using a small member type with custom copy/move that increments counters (so `Clip` itself still writes no
   special members).
2. `static Clip make_sine(std::string name, float freq, int n)` returning by value.
3. A `Playlist` that stores clips in a `std::vector<Clip>` via a sink `add(Clip c)`.
4. Show (by printing counters) that building a playlist of 3 clips performs **zero** copies.
""", solution=r'''
#include <cmath>
#include <iostream>
#include <numbers>
#include <string>
#include <utility>
#include <vector>

struct Tally {                       // instrumentation member: counts copies and moves of its owner
    inline static int copies = 0, moves = 0;
    Tally() = default;
    Tally(const Tally&) { ++copies; }
    Tally(Tally&&) noexcept { ++moves; }
    Tally& operator=(const Tally&) { ++copies; return *this; }
    Tally& operator=(Tally&&) noexcept { ++moves; return *this; }
};

class Clip {                         // Rule of Zero: no special members written
public:
    static Clip make_sine(std::string name, float freq, int n) {
        Clip c;
        c.name_ = std::move(name);
        c.samples_.reserve(static_cast<std::size_t>(n));
        for (int i = 0; i < n; ++i)
            c.samples_.push_back(std::sin(2.0f * std::numbers::pi_v<float> * freq * static_cast<float>(i) / 48000.0f));
        return c;                     // NRVO / implicit move
    }
    const std::string& name() const { return name_; }
    std::size_t size() const { return samples_.size(); }
private:
    std::string name_;
    std::vector<float> samples_;
    Tally tally_;
};

class Playlist {
public:
    void add(Clip c) { clips_.push_back(std::move(c)); }   // sink
    void print() const { for (const auto& c : clips_) std::cout << c.name() << '(' << c.size() << ") "; std::cout << '\n'; }
private:
    std::vector<Clip> clips_;
};

int main() {
    Playlist p;
    p.add(Clip::make_sine("A4", 440.0f, 480));
    p.add(Clip::make_sine("C5", 523.25f, 480));
    Clip e = Clip::make_sine("E5", 659.25f, 480);
    p.add(std::move(e));
    p.print();
    std::cout << "copies=" << Tally::copies << " moves=" << Tally::moves << '\n';
}
''', ))
