WEEK = dict(num=4, title="Classes and RAII", intro="""
This week we design our own types. A class bundles data with the operations that keep that data valid.
We'll see constructors and destructors, the (many!) ways C++ initializes objects, and then the single most
important idiom in the language: **RAII**, which ties resource cleanup to object lifetime.

If you only remember one thing from this course, make it RAII. It's why well-written C++ rarely leaks,
even without a garbage collector.
""", lessons=[
dict(title="Classes, encapsulation, and const member functions", std="C++20", minutes=10, area="OOP: classes",
features=[("`class` vs `struct`, `public`/`private`/`protected`", "C++98"), ("Member functions, `this`", "C++98"), ("`const` member functions, `mutable`", "C++98"), ("Class invariants", "—"), ("Ref-qualified member functions (`&`, `&&`)", "C++11")],
why="""
Imagine a `Volume` type whose value must always be between 0 and 100. If it's a plain struct with a public
`int`, any line of code anywhere can set it to -7, and you'll find out three weeks later in a bug report.
A class lets you make the data private and only allow changes through functions that keep the rule —
the *invariant* — true. That's encapsulation, and it's what makes large programs manageable.
""",
body="""
## `class` and `struct` are almost the same

The only difference: members of a `struct` are public by default; members of a `class` are private by
default. Convention: use `struct` for plain bundles of data with no invariants, and `class` when there's an
invariant to protect.

## Protecting an invariant

{{ex}}

Let's walk through the design:

- `level_` is **private**: only member functions can touch it.
- The constructor and `set()` both go through `clamp`, so the invariant "0 ≤ level ≤ 100" holds for every
  `Volume` that ever exists.
- `get()` is marked **`const`**: it promises not to modify the object. That's what allows it to be called
  on a `const Volume&`. Forgetting `const` on getters is a very common mistake — the moment someone has a
  `const` reference, your class becomes unusable.
- `this` is a pointer to the current object. You rarely need to write it explicitly.

## `mutable`: the escape hatch

Sometimes a `const` function legitimately needs to change something that isn't part of the observable state
— a cache, or a mutex. Mark that member `mutable`. Use it sparingly: it's for implementation details only.

## The wrong way: getters and setters for everything

```cpp
class Volume {
    int level_;
public:
    int  getLevel() const { return level_; }
    void setLevel(int l)  { level_ = l; }     // no checking: this is a struct with extra steps
};
```

A setter that doesn't enforce anything adds ceremony without protection. Either there's an invariant (then
enforce it) or there isn't (then use a plain struct).

## Ref-qualifiers (advanced, optional)

You can overload a member function on whether `*this` is an lvalue or an rvalue: `get() &` vs `get() &&`.
This lets a temporary give away its internals cheaply. You'll appreciate it after Week 5; C++23's
*deducing this* (Week 8) makes it much easier to write.
""",
files={"": r'''
#include <iostream>

class Volume {
public:
    explicit Volume(int level = 50) : level_{clamp(level)} {}

    void set(int level) { level_ = clamp(level); }
    void louder(int step = 10) { set(level_ + step); }
    int get() const { return level_; }          // const: callable on const objects
    bool muted() const { return level_ == 0; }

private:
    static int clamp(int v) { return v < 0 ? 0 : (v > 100 ? 100 : v); }
    int level_;                                  // invariant: 0 <= level_ <= 100
};

void show(const Volume& v) {                     // only const members are callable here
    std::cout << "volume " << v.get() << (v.muted() ? " (muted)" : "") << '\n';
}

int main() {
    Volume v{70};
    show(v);
    v.louder(); v.louder(); v.louder();
    show(v);                                     // clamped to 100
    v.set(-5);
    show(v);                                     // clamped to 0
}
'''},
takeaways=["`class` and `struct` differ only in default access; use `class` when you have an invariant.",
"Make data private and enforce invariants in constructors and member functions.",
"Mark every member function that doesn't modify the object `const`.",
"`mutable` is for caches/mutexes — not for avoiding thinking about const."],
quiz=[("Why can't you call a non-const member function through a `const Volume&`?", "A const reference only allows operations that promise not to modify the object, i.e. `const` member functions."),
("What's the type of `this` inside a `const` member function of `Volume`?", "`const Volume*`."),
("When is a plain `struct` with public members the right choice?", "When the members are independent and any combination of values is valid — there's no invariant to protect.")]),

dict(title="Constructors, destructors, and every way to initialize", std="C++20", minutes=12, area="OOP: classes",
features=[("Constructors, member initializer lists", "C++98"), ("Default member initializers", "C++11"), ("Delegating constructors", "C++11"), ("`= default`, `= delete`", "C++11"), ("Member initialization order = declaration order", "C++98"), ("List-initialization and the `std::initializer_list` constructor pitfall", "C++11"), ("Value-, default-, zero-initialization; most vexing parse", "C++11"), ("Destructors", "C++98")],
why="""
C++ has a famously large number of ways to initialize an object — `T x;`, `T x{};`, `T x();`, `T x = y;`,
`T x(a, b);`, `T x{a, b};` — and some of them do surprisingly different things. This lesson doesn't try to
list every rule. Instead it gives you a small set of habits that are always right, and shows you the three
traps that catch everyone.
""",
body="""
## Constructors and the member initializer list

A constructor runs when an object is created. Members should be initialized in the **member initializer
list** (after the `:`), not assigned in the body:

```cpp
class Track {
    std::string title_;
    int length_s_;
public:
    Track(std::string t, int len) : title_{std::move(t)}, length_s_{len} {}   // initialize
    // Track(std::string t, int len) { title_ = t; length_s_ = len; }        // default-construct, then assign
};
```

The second version first default-constructs `title_` and then assigns — wasted work, and impossible for
`const` members, references, or types with no default constructor.

## Default member initializers, delegation, `= default` and `= delete`

{{ex}}

- **Default member initializers** (`int channels_ = 2;`) give a value whenever a constructor doesn't
  mention that member. They remove a lot of repetition.
- **Delegating constructors** call another constructor of the same class.
- `= default` asks for the compiler-generated version; `= delete` forbids an operation (here: no
  construction from `bool`, which would otherwise convert silently to `int`).
- The **destructor** `~Stream()` runs when the object's lifetime ends. Order: the destructor body runs, then
  members are destroyed in *reverse declaration order*.

!!! warning "A real surprise we hit while writing this lesson"
    Our first draft said `Stream b{"speaker"};` — and it **failed to compile** with "call to deleted
    constructor". Why? A string literal is a `const char*`, and `const char*` → `bool` is a *standard*
    conversion, which beats the *user-defined* conversion `const char*` → `std::string`. So overload
    resolution picked `Stream(bool)`. Without the `= delete`, it would have silently compiled and called the
    wrong constructor. That's precisely why deleting the `bool` overload is a good idea — and why
    `std::string_view` parameters are often friendlier than `std::string` ones.

## Trap 1: members are initialized in declaration order

```cpp
class Buffer {
    std::size_t size_;
    std::vector<int> data_;
public:
    Buffer(std::size_t n) : data_(n), size_(data_.size()) {}  // looks fine...
};
```

This works by luck. But swap the declarations of `size_` and `data_` and `data_(size_)` would read an
uninitialized `size_`. Members are **always** initialized in the order they're *declared*, regardless of the
order in the initializer list. `-Wall` warns (`-Wreorder`) when the orders differ — listen to it.

## Trap 2: braces prefer `std::initializer_list`

```cpp
std::vector<int> a(3, 7);   // three elements: 7 7 7
std::vector<int> b{3, 7};   // two elements: 3 7  (initializer_list constructor wins)
```

If a class has an `initializer_list` constructor, brace-init strongly prefers it. Use parentheses when you
mean "call the size constructor".

## Trap 3: the most vexing parse

```cpp
Stream s();      // NOT an object! Declares a function named s returning Stream.
Stream s{};      // value-initialized object. Use braces.
```

## Habits that are always right

1. Give every member a default member initializer or initialize it in every constructor.
2. Use `T x{...};` for objects, but `( )` when you need a specific non-list constructor of a container.
3. Use `{}` to value-initialize (`int x{};` is 0; `T t{};` runs the default constructor or zero-fills).
4. Mark single-argument constructors `explicit` (next lesson).
""",
files={"": r'''
#include <iostream>
#include <string>
#include <utility>
#include <vector>

class Stream {
public:
    Stream(std::string name, int rate) : name_{std::move(name)}, rate_{rate} {
        std::cout << "open " << name_ << " @" << rate_ << " ch=" << channels_ << '\n';
    }
    explicit Stream(std::string name) : Stream(std::move(name), 48'000) {}   // delegating
    Stream(bool) = delete;                                                  // forbid Stream(true)
    ~Stream() { std::cout << "close " << name_ << '\n'; }

private:
    std::string name_;
    int rate_;
    int channels_ = 2;     // default member initializer
};

struct Point { int x = 0, y = 0; Point() = default; Point(int x_, int y_) : x{x_}, y{y_} {} };

int main() {
    Stream a{"mic", 16'000};
    Stream b{std::string{"speaker"}};   // see the "surprise" box: Stream b{"speaker"} would pick Stream(bool)!

    std::vector<int> paren(3, 7), brace{3, 7};
    std::cout << "paren size=" << paren.size() << " brace size=" << brace.size() << '\n';

    int zero{};         // value-initialized: 0
    Point p{};          // default constructor
    Point q{1, 2};
    std::cout << zero << ' ' << p.x << ',' << p.y << ' ' << q.x << ',' << q.y << '\n';
}   // b closes first, then a
''', "_bad": {"expect": "fail", "code": r'''
// Wrong way: a deleted constructor can't be called.
#include <string>
class Stream {
public:
    explicit Stream(int) {}
    Stream(bool) = delete;
};
int main() {
    Stream s{true};   // error: use of deleted function
}
'''}},
takeaways=["Initialize members in the member initializer list (or with default member initializers), don't assign in the body.",
"Members are initialized in declaration order, whatever order you write the list in.",
"Brace-init prefers `initializer_list` constructors: `vector<int>{3,7}` has two elements.",
"`T x();` declares a function; write `T x{};`.",
"`= default` and `= delete` control which special operations exist."],
quiz=[("How many elements does `std::vector<int> v{5};` have? And `std::vector<int> v(5);`?", "`{5}`: one element with value 5 (initializer_list). `(5)`: five zero-valued elements."),
("A class declares `int a_; int b_;` and the constructor writes `: b_{1}, a_{b_}`. What's `a_`?", "Indeterminate (UB to read): `a_` is initialized first, from the not-yet-initialized `b_`. Initialization follows declaration order."),
("Why might you `= delete` a constructor taking `bool`?", "To stop accidental implicit conversions (e.g. a pointer or bool converting to int) from silently selecting another constructor.")]),

dict(title="RAII: tying resources to object lifetime", std="C++20", minutes=12, area="OOP: classes",
features=[("RAII (Resource Acquisition Is Initialization)", "C++98"), ("Destructors run during stack unwinding", "C++98"), ("Scope guards", "—"), ("Wrapping C handles (FILE*, fds) in RAII types", "—"), ("Non-copyable resource types", "C++11")],
why="""
Suppose you open a file, lock a mutex, or grab a hardware codec. Then something goes wrong halfway
through — an early `return`, an exception. Who releases the resource? In C you write `goto cleanup` and
hope you covered every path. In C++ the answer is beautiful: *the destructor does*, automatically, on every
path. This idea is called RAII, and it's the most important idiom in C++.
""",
body="""
## The wrong way: manual cleanup

```cpp
bool save(const char* path, const Data& d) {
    std::FILE* f = std::fopen(path, "wb");
    if (!f) return false;
    if (!write_header(f, d)) return false;       // LEAK: forgot fclose
    write_body(f, d);                            // if this throws: LEAK
    std::fclose(f);
    return true;
}
```

Every new exit path is a chance to forget cleanup.

## RAII: acquire in the constructor, release in the destructor

The trick is to wrap the resource in a small class whose destructor releases it. Because destructors of
local objects run whenever a scope is left — normal flow, `return`, `break`, or an exception unwinding
the stack — cleanup happens on *every* path, with no extra code at the call site.

{{ex}}

Look at the output: when the exception propagates out of `process`, the `File` destructor still runs
before the `catch` block. That's **stack unwinding**.

A few design points in that `File` class:

- The copy operations are `= delete`d. Two `File` objects owning the same `FILE*` would both call
  `fclose` — a double close. (In Week 5 we'll make it *movable* so ownership can be transferred.)
- The constructor throws if it can't acquire the resource. That way, a `File` object that exists is always
  a valid, open file: a class invariant.

## RAII is everywhere in the standard library

| Resource | RAII type |
|---|---|
| heap memory | `std::vector`, `std::string`, `std::unique_ptr`, `std::shared_ptr` |
| mutex lock | `std::lock_guard`, `std::scoped_lock`, `std::unique_lock` |
| thread | `std::jthread` (joins in its destructor) |
| file | `std::fstream` |

You can also make a general **scope guard** — an object that runs a lambda in its destructor — for one-off
cleanup actions. The example includes a tiny one.

!!! tip "Pro tip: Android & C APIs"
    NDK APIs are C APIs: `AMediaCodec_delete`, `AAsset_close`, `ANativeWindow_release`... Wrap each in an
    RAII type (or `std::unique_ptr` with a custom deleter, Week 12) once, and your JNI code stops leaking.
""",
files={"": r'''
#include <cstdio>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>

class File {
public:
    File(const char* path, const char* mode) : f_{std::fopen(path, mode)} {
        if (!f_) throw std::runtime_error(std::string{"cannot open "} + path);
        std::cout << "  opened " << path << '\n';
    }
    ~File() { std::fclose(f_); std::cout << "  closed\n"; }
    File(const File&) = delete;              // one owner only
    File& operator=(const File&) = delete;

    void write(const std::string& s) { std::fputs(s.c_str(), f_); }

private:
    std::FILE* f_;
};

template <class F>
class ScopeGuard {                           // runs an action when the scope ends
public:
    explicit ScopeGuard(F f) : f_{std::move(f)} {}
    ~ScopeGuard() { f_(); }
    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;
private:
    F f_;
};

void process(bool fail) {
    File out{"/tmp/raii_demo.txt", "w"};
    ScopeGuard guard{[] { std::cout << "  guard: cleanup step\n"; }};
    out.write("hello\n");
    if (fail) throw std::runtime_error("encoding failed");
    std::cout << "  done\n";
}

int main() {
    std::cout << "normal run:\n";
    process(false);
    std::cout << "failing run:\n";
    try {
        process(true);
    } catch (const std::exception& e) {
        std::cout << "  caught: " << e.what() << '\n';
    }
}
'''},
takeaways=["RAII: acquire a resource in a constructor, release it in the destructor.",
"Destructors run on every exit path, including exceptions (stack unwinding).",
"A resource-owning class must decide its copy behaviour; often `= delete` copies (and allow moves).",
"The standard library is RAII all the way down; wrap C handles the same way."],
quiz=[("Why does RAII make code exception-safe without try/catch at every call site?", "Destructors of local objects run during stack unwinding, so resources are released whatever path leaves the scope."),
("What goes wrong if a `File` RAII class is copyable with the default copy constructor?", "Both copies hold the same `FILE*` and both destructors call `fclose` on it — a double close (UB)."),
("Name three RAII types from the standard library.", "For example `std::vector`, `std::unique_ptr`, `std::lock_guard`, `std::jthread`, `std::fstream`.")],
lab=dict(task="""
Write an RAII class `Timer` that records `std::chrono::steady_clock::now()` in its constructor and prints the
elapsed milliseconds (with a label) in its destructor. Use it to time a loop. Make it non-copyable.
""", solution={"compare": False, "code": r'''
#include <chrono>
#include <iostream>
#include <string>
#include <utility>

class Timer {
public:
    explicit Timer(std::string label) : label_{std::move(label)}, start_{std::chrono::steady_clock::now()} {}
    ~Timer() {
        const auto ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - start_);
        std::cout << label_ << ": " << ms.count() << " ms\n";
    }
    Timer(const Timer&) = delete;
    Timer& operator=(const Timer&) = delete;
private:
    std::string label_;
    std::chrono::steady_clock::time_point start_;
};

int main() {
    volatile double sink = 0;   // volatile so the loop isn't optimized away
    {
        Timer t{"sum loop"};
        for (int i = 0; i < 1'000'000; ++i) sink = sink + i * 0.5;
    }
}
'''})),

dict(title="explicit, conversions, static members, friends, nested classes", std="C++20", minutes=11, area="OOP: classes",
features=[("`explicit` constructors and `explicit(bool)`", "C++20"), ("Conversion operators, `explicit operator bool`", "C++11"), ("`static` data members and functions, `inline static`", "C++17"), ("`friend` functions and classes", "C++98"), ("Nested classes and local classes", "C++98")],
why="""
Here's a real surprise: `void play(Duration d);` ... `play(5);` compiles, and plays for 5 *what*? If
`Duration` has a constructor taking an `int`, C++ will quietly convert. Implicit conversions are
sometimes great (`std::string s = "hi";`) and sometimes a bug factory. This lesson is about controlling
them, plus a few other class features you'll meet constantly.
""",
body="""
## `explicit`: no surprise conversions

A constructor that can be called with one argument is a *converting constructor*: the compiler may use it
implicitly. Mark it `explicit` unless the conversion is truly natural and lossless.

```cpp
struct Millis { explicit Millis(long v) : value{v} {} long value; };
void sleep_for(Millis);
sleep_for(5);           // ERROR (good!) — what unit is 5?
sleep_for(Millis{5});   // clear
```

C++20 added `explicit(condition)` for generic code, e.g. "explicit only if the conversion is narrowing".

## Conversion operators

The reverse direction: `operator T() const` lets your type convert *to* `T`. The most common one is
`explicit operator bool()` — it works in `if (x)` and `!x` (contextual conversion) but won't let your
object silently become `1` in arithmetic.

## `static` members: belong to the class, not an object

A `static` data member has one instance shared by all objects; a `static` member function has no `this`.
Since C++17 you can define it inline: `inline static int count = 0;`.

## `friend`

A `friend` declaration grants a function or class access to private members. It's not a hack — it's the
right tool for operators that are naturally non-members (like `operator<<`) and for tightly coupled
helper classes. Keep friends few and close.

## Nested and local classes

A class defined inside another (`Playlist::Iterator`) is a *nested class*: it's scoped by the outer class
and can access its private members. A class defined inside a function is a *local class* — handy for
one-off helpers, though lambdas usually do the job.

{{ex}}

!!! warning "Common pitfall: implicit `operator bool`"
    Pre-C++11 code used `operator void*()` or non-explicit `operator bool()` hacks, which allowed
    nonsense like `stream1 + stream2`. Always write `explicit operator bool() const`.
""",
files={"": r'''
#include <iostream>
#include <string>
#include <utility>
#include <vector>

class Millis {
public:
    explicit Millis(long v) : value_{v} {}
    long count() const { return value_; }
private:
    long value_;
};

class Codec {
public:
    explicit Codec(std::string name) : name_{std::move(name)} { ++instances; }
    ~Codec() { --instances; }
    Codec(const Codec&) = delete;
    Codec& operator=(const Codec&) = delete;

    explicit operator bool() const { return !name_.empty(); }   // "is valid?"
    inline static int instances = 0;                              // shared by all Codecs

    friend std::ostream& operator<<(std::ostream& os, const Codec& c) {   // friend: sees name_
        return os << "Codec(" << c.name_ << ")";
    }

    struct Stats { int frames = 0; };                              // nested class
    Stats stats;
private:
    std::string name_;
};

void wait(Millis m) { std::cout << "wait " << m.count() << " ms\n"; }

int main() {
    wait(Millis{20});
    // wait(20);   // would not compile: constructor is explicit

    Codec opus{"opus"}, none{""};
    std::cout << opus << " valid=" << static_cast<bool>(opus) << ", none valid=" << (none ? "yes" : "no")
              << ", instances=" << Codec::instances << '\n';

    struct Counter { int n = 0; void hit() { ++n; } };             // local class
    Counter c;
    for (int i = 0; i < 3; ++i) c.hit();
    opus.stats.frames = c.n;
    std::cout << "frames=" << opus.stats.frames << '\n';
}
'''},
takeaways=["Mark single-argument constructors `explicit` unless the conversion is obviously safe.",
"Write `explicit operator bool()`; it still works in `if` and `!`.",
"`static` members belong to the class; `inline static` (C++17) defines them in the class body.",
"`friend` is the normal way to write non-member operators that need private access."],
quiz=[("Why does `if (codec)` compile with an `explicit operator bool`, but `int n = codec;` doesn't?", "`if` performs a *contextual conversion* to bool, which is allowed to use explicit conversion operators. Copy-initialization of `int` would need an implicit conversion."),
("Does a `static` member function have a `this` pointer?", "No; it isn't called on an object. It can access only static members (or objects passed to it)."),
("When is `friend` appropriate?", "For non-member functions that are part of a class's interface and need private access (e.g. `operator<<`, symmetric binary operators), or tightly coupled helper classes.")]),

dict(title="Operator overloading and the spaceship operator <=>", std="C++23", minutes=12, area="OOP: classes",
features=[("Operator overloading: member vs non-member, canonical forms", "C++98"), ("Three-way comparison `operator<=>`", "C++20"), ("Defaulted comparisons `= default`", "C++20"), ("`std::strong_ordering`, `weak_ordering`, `partial_ordering`", "C++20"), ("Rewritten comparison candidates (`a != b` from `==`)", "C++20"), ("Overloading `[]` (multi-dimensional subscript in C++23), `()`", "C++23")],
why="""
Suppose you have a `Version{major, minor, patch}` and want to sort a list of them, or check
`if (v >= Version{2, 1, 0})`. Before C++20 that meant writing six comparison operators by hand, carefully
keeping them consistent. Now it's one line. Operator overloading lets your types feel like built-in ones —
let's see how to do it well, and what *not* to do.
""",
body="""
## The basic idea

An operator is just a function with a special name: `a + b` calls `operator+(a, b)` (or `a.operator+(b)`).
The rules of thumb, from the C++ Core Guidelines and decades of experience:

- **Do what the built-in operator would do.** `+` adds, `==` compares. No clever surprises.
- **Binary operators that treat both sides symmetrically should be non-members** (often `friend`s),
  so conversions apply to both operands.
- **Implement `+` in terms of `+=`.**

## Comparisons in C++20: `<=>` and `= default`

```cpp
struct Version {
    int major, minor, patch;
    auto operator<=>(const Version&) const = default;   // gives <, <=, >, >=
    bool operator==(const Version&) const = default;    // gives ==, != (implied by <=> = default too)
};
```

That defaulted `<=>` compares members in declaration order (lexicographically), exactly what you want for
versions. The result is a *comparison category*:

| Category | Meaning | Example |
|---|---|---|
| `std::strong_ordering` | equal values are indistinguishable | `int` |
| `std::weak_ordering` | equivalent values may differ | case-insensitive strings |
| `std::partial_ordering` | some values are unordered | `double` (NaN) |

C++20 also *rewrites* expressions: `a != b` becomes `!(a == b)`, and `a < b` can use `(a <=> b) < 0`,
including with the arguments reversed. So you write two functions and get all six operators.

{{ex}}

## Arithmetic operators

The canonical pattern, shown for a 2D vector in the example: a member `operator+=` that modifies `*this`
and returns `*this` by reference, and a non-member `operator+` that takes its left operand **by value**,
uses `+=`, and returns it.

## Other operators you'll overload

- `operator[]` for containers. C++23 allows multiple arguments: `m[i, j]`.
- `operator()` makes a *function object* (functor) — the idea behind lambdas.
- `operator<<` with `std::ostream` for printing.

## The wrong way: surprising operators

```cpp
Matrix operator*(const Matrix&, const Matrix&);   // fine: math
Logger& operator<<(Logger&, Level);               // fine: established stream idiom
bool operator&&(const A&, const B&);              // AVOID: loses short-circuit evaluation
Thing& operator,(Thing&, Thing&);                 // AVOID: nobody expects this
```

Overloaded `&&`, `||` and `,` don't short-circuit / sequence the way the built-ins do. Don't overload them.
""",
files={"": r'''
#include <algorithm>
#include <compare>
#include <iostream>
#include <vector>

struct Version {
    int major = 0, minor = 0, patch = 0;
    auto operator<=>(const Version&) const = default;   // all six comparisons
    friend std::ostream& operator<<(std::ostream& os, const Version& v) {
        return os << v.major << '.' << v.minor << '.' << v.patch;
    }
};

struct Vec2 {
    double x = 0, y = 0;
    Vec2& operator+=(const Vec2& o) { x += o.x; y += o.y; return *this; }
    friend Vec2 operator+(Vec2 a, const Vec2& b) { return a += b; }   // a is a copy
    friend Vec2 operator*(double k, Vec2 v) { v.x *= k; v.y *= k; return v; }
    bool operator==(const Vec2&) const = default;
};

class Grid {
public:
    int& operator[](int r, int c) { return cells_[static_cast<std::size_t>(r * 3 + c)]; }   // C++23 multi-arg []
private:
    std::vector<int> cells_ = std::vector<int>(9);
};

int main() {
    std::vector<Version> vs{{2, 1, 0}, {1, 9, 9}, {2, 0, 5}, {2, 1, 0}};
    std::ranges::sort(vs);
    for (const auto& v : vs) std::cout << v << ' ';
    std::cout << '\n' << std::boolalpha
              << (Version{2, 1, 0} >= Version{2, 0, 5}) << ' ' << (vs[2] == vs[3]) << ' '
              << (vs[0] != vs[1]) << '\n';

    auto r = (1.5 <=> 2.0);
    std::cout << "1.5 <=> 2.0 is less? " << (r < 0) << '\n';

    Vec2 a{1, 2}, b{3, 4};
    Vec2 c = a + b;
    Vec2 d = 2.0 * c;
    std::cout << c.x << ',' << c.y << ' ' << d.x << ',' << d.y << ' ' << (c == Vec2{4, 6}) << '\n';

    Grid g;
    g[1, 2] = 7;
    std::cout << "g[1, 2] = " << g[1, 2] << '\n';
}
'''},
takeaways=["Overload operators only with their conventional meaning.",
"In C++20, `auto operator<=>(const T&) const = default;` gives all six comparisons, member-wise.",
"Comparison categories: strong, weak, partial ordering.",
"Implement `+` via `+=`; make symmetric binary operators non-members.",
"Never overload `&&`, `||` or `,`."],
quiz=[("With only `bool operator==(const T&) const` defined, does `a != b` compile in C++20?", "Yes. C++20 rewrites `a != b` as `!(a == b)`."),
("What comparison category does `double <=> double` return and why?", "`std::partial_ordering`, because NaN is unordered with respect to every value."),
("Why take the left operand of `operator+` by value?", "We need a copy to modify anyway; taking it by value lets the compiler move from temporaries and makes the implementation `return a += b;`."),
("Why shouldn't you overload `operator&&`?", "The overloaded version is a normal function call: both operands are always evaluated, so short-circuiting is lost.")]),
],
assignment=dict(title="A Rational number type", task="""
Implement `class Rational` (numerator/denominator, `long long`):

1. Invariant: denominator > 0 and the fraction is always reduced (use `std::gcd` from `<numeric>`).
   The constructor throws `std::invalid_argument` on a zero denominator.
2. `+ - * /` via the compound-assignment pattern; `explicit operator double()`.
3. Comparisons with `<=>` — careful: a defaulted `<=>` would compare numerators first, which is wrong for
   fractions! Write a custom `operator<=>` that cross-multiplies, plus a defaulted `operator==` (correct
   because fractions are always reduced).
4. `operator<<` printing `3/4`.
""", solution=r'''
#include <compare>
#include <iostream>
#include <numeric>
#include <stdexcept>

class Rational {
public:
    Rational(long long n = 0, long long d = 1) : num_{n}, den_{d} {   // implicit from integers is natural here
        if (den_ == 0) throw std::invalid_argument("zero denominator");
        normalize();
    }
    long long num() const { return num_; }
    long long den() const { return den_; }

    Rational& operator+=(const Rational& o) { num_ = num_ * o.den_ + o.num_ * den_; den_ *= o.den_; normalize(); return *this; }
    Rational& operator-=(const Rational& o) { return *this += Rational{-o.num_, o.den_}; }
    Rational& operator*=(const Rational& o) { num_ *= o.num_; den_ *= o.den_; normalize(); return *this; }
    Rational& operator/=(const Rational& o) { return *this *= Rational{o.den_, o.num_}; }

    friend Rational operator+(Rational a, const Rational& b) { return a += b; }
    friend Rational operator-(Rational a, const Rational& b) { return a -= b; }
    friend Rational operator*(Rational a, const Rational& b) { return a *= b; }
    friend Rational operator/(Rational a, const Rational& b) { return a /= b; }

    bool operator==(const Rational&) const = default;   // OK: always reduced
    std::strong_ordering operator<=>(const Rational& o) const { return num_ * o.den_ <=> o.num_ * den_; }

    explicit operator double() const { return static_cast<double>(num_) / static_cast<double>(den_); }
    friend std::ostream& operator<<(std::ostream& os, const Rational& r) { return os << r.num_ << '/' << r.den_; }

private:
    void normalize() {
        if (den_ < 0) { num_ = -num_; den_ = -den_; }
        const long long g = std::gcd(num_, den_);
        if (g > 1) { num_ /= g; den_ /= g; }
    }
    long long num_, den_;
};

int main() {
    Rational a{1, 2}, b{3, -4};
    std::cout << a << " + " << b << " = " << a + b << '\n';
    std::cout << a << " * " << b << " = " << a * b << '\n';
    std::cout << a << " / " << b << " = " << a / b << '\n';
    std::cout << std::boolalpha << (Rational{2, 4} == a) << ' ' << (b < a) << ' ' << (a + 1 > Rational{3, 2}) << '\n';
    std::cout << static_cast<double>(Rational{1, 3}) << '\n';
    try { Rational bad{1, 0}; } catch (const std::invalid_argument& e) { std::cout << "error: " << e.what() << '\n'; }
}
'''))
