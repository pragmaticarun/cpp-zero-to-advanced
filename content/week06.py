WEEK = dict(num=6, title="Inheritance and runtime polymorphism", intro="""
This week covers classic object-oriented C++: base and derived classes, virtual functions, and how the
compiler implements them with vtables. We'll also look at the traps — slicing, missing virtual
destructors — and at multiple inheritance and RTTI.

A modern perspective runs through the week: inheritance is a tool for *runtime polymorphism*, not for code
reuse. In Weeks 7–8 and 16 you'll see alternatives (templates, `std::variant`, type erasure) and learn when
each fits.
""", lessons=[
dict(title="Inheritance basics: base classes, access, construction order", std="C++20", minutes=10, area="OOP: inheritance & polymorphism",
features=[("Public/protected/private inheritance", "C++98"), ("Construction/destruction order of bases and members", "C++98"), ("Calling base constructors; inheriting constructors `using Base::Base`", "C++11"), ("Name hiding in derived classes, `using Base::f`", "C++98"), ("`protected` members", "C++98")],
why="""
Suppose every audio effect in your app — gain, echo, low-pass filter — has a name, an enabled flag and a
bypass switch. Writing those three things in every class is tedious and error-prone. Inheritance lets a
derived class *be a kind of* base class and get its members. Let's see the mechanics first; next lesson
we'll add the real superpower, virtual functions.
""",
body="""
## Is-a relationships

```cpp
class Effect { ... };                 // base class
class Gain : public Effect { ... };   // Gain *is an* Effect
```

With **public** inheritance, a `Gain` can be used wherever an `Effect&` or `Effect*` is expected. That's
the only kind of inheritance you'll use regularly. (`private` inheritance means "implemented in terms of"
and is rare; prefer a member.)

| Base member is... | accessible in derived? | accessible to users of derived (public inheritance)? |
|---|---|---|
| `public` | yes | yes |
| `protected` | yes | no |
| `private` | no | no |

## Construction order

A derived object contains a base *subobject*. Construction goes **base first, then members (in
declaration order), then the derived constructor body**. Destruction runs in exactly the reverse order.
You call a base constructor from the member initializer list. If the derived class adds no state of its own,
`using Base::Base;` (C++11) inherits the base constructors.

{{ex}}

## The wrong way: name hiding

```cpp
struct Base    { void process(int); void process(double); };
struct Derived : Base { void process(int); };   // hides BOTH Base::process overloads
Derived d; d.process(2.5);                     // calls Derived::process(int) with 2 — surprise!
```

Declaring any `process` in `Derived` hides all of the base's `process` overloads. Bring them back with
`using Base::process;` in `Derived`.

!!! tip "Pro tip: prefer composition"
    "Has-a" is usually a member; "is-a" is inheritance. If you inherit only to reuse code, a member object
    is almost always simpler and more flexible.
""",
files={"": r'''
#include <iostream>
#include <string>
#include <utility>

struct Tracer {
    std::string name;
    explicit Tracer(std::string n) : name{std::move(n)} { std::cout << "  + " << name << '\n'; }
    ~Tracer() { std::cout << "  - " << name << '\n'; }
};

class Effect {
public:
    explicit Effect(std::string name) : name_{std::move(name)}, t_{"Effect base"} {}
    const std::string& name() const { return name_; }
    bool enabled() const { return enabled_; }
    void set_enabled(bool e) { enabled_ = e; }
    void process(int n) { std::cout << "  Effect::process(int " << n << ")\n"; }
    void process(double x) { std::cout << "  Effect::process(double " << x << ")\n"; }
protected:
    int processed_ = 0;                 // visible to derived classes only
private:
    std::string name_;
    bool enabled_ = true;
    Tracer t_;
};

class Gain : public Effect {
public:
    Gain(float g) : Effect{"gain"}, t_{"Gain member"}, gain_{g} { std::cout << "  Gain body\n"; }
    using Effect::process;              // un-hide the base overloads
    void process(float x) { ++processed_; std::cout << "  Gain::process(float " << x * gain_ << ")\n"; }
private:
    Tracer t_;
    float gain_;
};

class Mute : public Effect {
public:
    using Effect::Effect;               // inherit constructors
};

int main() {
    std::cout << "construct:\n";
    {
        Gain g{2.0f};
        g.process(1.5f);
        g.process(7);                   // Effect::process(int), thanks to `using`
        Mute m{"mute"};
        std::cout << "  " << g.name() << ' ' << m.name() << '\n';
        std::cout << "destroy:\n";
    }
}
'''},
takeaways=["Public inheritance models *is-a*; a derived object contains a base subobject.",
"Construction: bases, then members in declaration order, then the body; destruction is the reverse.",
"A member function in a derived class hides all base overloads with that name; `using Base::f;` restores them.",
"Prefer composition for code reuse."],
quiz=[("In what order are these constructed: base `B`, members `m1`, `m2` of derived `D`, and `D`'s constructor body?", "`B`, then `m1`, then `m2` (declaration order), then the body of `D`'s constructor."),
("What does `using Base::Base;` do?", "Inherits Base's constructors into the derived class (C++11)."),
("Why might `d.process(2.5)` call `Derived::process(int)`?", "Because `Derived` declares `process`, which hides all `Base::process` overloads; the only candidate takes `int` and 2.5 converts to it.")]),

dict(title="Virtual functions, override, final, and how vtables work", std="C++20", minutes=12, area="OOP: inheritance & polymorphism",
features=[("Virtual functions and dynamic dispatch", "C++98"), ("`override` and `final`", "C++11"), ("Vtables and vptr (implementation model)", "—"), ("Virtual calls in constructors/destructors", "C++98"), ("Covariant return types", "C++98"), ("Devirtualization", "—")],
why="""
Now the payoff. You have a `std::vector<Effect*>` holding a gain, an echo and a filter, and you want
`for (auto* e : chain) e->process(buffer);` to call *the right* `process` for each one. That's
**dynamic dispatch**, and it's what `virtual` gives you. Let's also peek under the hood, because knowing
how it works tells you exactly what it costs.
""",
body="""
## `virtual` and `override`

```cpp
struct Effect {
    virtual ~Effect() = default;
    virtual void process(std::span<float> buf) = 0;   // (= 0: pure virtual; next lesson)
};
struct Gain : Effect {
    void process(std::span<float> buf) override { ... }
};
```

When a function is `virtual`, a call through a base reference or pointer runs the *most-derived override*
at run time. Always write `override` on overrides: if the signature doesn't actually match (a missing
`const`, a different parameter type), the compiler errors instead of silently creating a new, unrelated
function.

```cpp
struct Base { virtual void draw() const; };
struct Oops : Base { void draw(); };            // WRONG: no const -> a new function, not an override
struct Good : Base { void draw() const override; };
```

`final` on a function stops further overriding; on a class, stops inheritance. It also helps the
optimizer *devirtualize* calls.

{{ex}}

## How it works: vtables

The standard doesn't say, but every mainstream compiler does the same thing:

- Each class with virtual functions has a static table, the **vtable**, holding pointers to its versions of
  each virtual function.
- Each object of such a class holds a hidden pointer, the **vptr**, to its class's vtable (that's why
  `sizeof` grew by 8 in the output).
- A virtual call is: load the vptr, load the function pointer from a fixed slot, call it.

```mermaid
flowchart LR
  O[Gain object: vptr + gain_] --> V[Gain vtable: ~Gain, process, name]
  V --> F1[Gain::process]
  V --> F2[Effect::name]
```

So the cost is one or two extra loads and an indirect call, plus — more importantly — the call usually
**can't be inlined**. In a per-sample inner loop that matters; per buffer, it's noise. Design accordingly:
make virtual calls coarse-grained (process a whole buffer, not one sample).

## Virtual calls in constructors and destructors

During `Effect`'s constructor, the object is *only* an `Effect` yet — the derived part doesn't exist. A
virtual call there calls `Effect`'s version, not the derived one. The example shows this.
""",
files={"": r'''
#include <iostream>
#include <memory>
#include <span>
#include <string>
#include <vector>

class Effect {
public:
    Effect() { std::cout << "Effect ctor sees name(): " << name() << '\n'; }   // calls Effect::name!
    virtual ~Effect() = default;
    virtual void process(std::span<float> buf) = 0;
    virtual std::string name() const { return "effect"; }
};

class Gain final : public Effect {
public:
    explicit Gain(float g) : g_{g} {}
    void process(std::span<float> buf) override { for (auto& x : buf) x *= g_; }
    std::string name() const override { return "gain"; }
private:
    float g_;
};

class Clip : public Effect {
public:
    void process(std::span<float> buf) override {
        for (auto& x : buf) x = x > 1.0f ? 1.0f : (x < -1.0f ? -1.0f : x);
    }
    std::string name() const override { return "clip"; }
};

struct NoVirtual { float g; };
struct WithVirtual { virtual ~WithVirtual() = default; float g; };

int main() {
    std::vector<std::unique_ptr<Effect>> chain;
    chain.push_back(std::make_unique<Gain>(3.0f));
    chain.push_back(std::make_unique<Clip>());

    std::vector<float> buf{0.1f, 0.5f, -0.6f};
    for (const auto& e : chain) {          // dynamic dispatch
        e->process(buf);
        std::cout << e->name() << ": ";
        for (float x : buf) std::cout << x << ' ';
        std::cout << '\n';
    }
    std::cout << "sizeof(NoVirtual)=" << sizeof(NoVirtual) << " sizeof(WithVirtual)=" << sizeof(WithVirtual) << '\n';
}
''', "_bad": {"expect": "fail", "code": r'''
// Wrong way: `override` catches a signature mismatch (missing const).
struct Base { virtual ~Base() = default; virtual void draw() const {} };
struct Oops : Base { void draw() override {} };   // error: does not override
int main() {}
'''}},
takeaways=["`virtual` + a base pointer/reference = the most-derived override runs at run time.",
"Always mark overrides `override`; use `final` to forbid further overriding.",
"Vtable model: one table per class, one hidden vptr per object; virtual calls block inlining.",
"In constructors and destructors, virtual calls resolve to the current class, not the derived one."],
quiz=[("What does `override` buy you?", "A compile error if the function doesn't actually override a base virtual function (e.g. signature mismatch), instead of a silent new function."),
("Why did `sizeof(WithVirtual)` grow?", "Objects of a polymorphic class carry a hidden vptr (8 bytes on 64-bit), plus padding for alignment."),
("What's the main performance cost of a virtual call?", "Usually not the indirect call itself but the lost inlining and optimization across the call; also possible branch mispredictions. Keep virtual calls coarse-grained.")]),

dict(title="Abstract classes, interfaces, virtual destructors, and slicing", std="C++20", minutes=11, area="OOP: inheritance & polymorphism",
features=[("Pure virtual functions, abstract classes", "C++98"), ("Interfaces as abstract base classes", "—"), ("Virtual destructors (and when not to)", "C++98"), ("Object slicing", "C++98"), ("Polymorphic copy: `clone()`", "—"), ("Non-virtual interface (NVI) idiom", "—")],
why="""
Two bugs show up in almost every codebase that uses inheritance. First: deleting a derived object through a
base pointer, and the derived destructor never runs — a leak. Second: copying a derived object into a base
*value*, and losing everything that made it derived. Both are easy to prevent once you've seen them. Let's
see them.
""",
body="""
## Abstract classes and interfaces

A **pure virtual** function (`= 0`) has no implementation in the base; a class with one is **abstract** and
can't be instantiated. A class with only pure virtual functions (and a virtual destructor) is C++'s version
of an *interface*:

```cpp
class AudioSink {
public:
    virtual ~AudioSink() = default;
    virtual void write(std::span<const float>) = 0;
};
```

## Bug 1: no virtual destructor

```cpp
struct Base { ~Base() {} };                        // not virtual
struct Derived : Base { std::vector<int> big; };
Base* p = new Derived;
delete p;     // UB: only ~Base runs; Derived's members are never destroyed
```

**Rule:** a base class meant for polymorphic deletion needs a `public virtual` destructor. (If instead you
never delete through the base, make the base destructor `protected` and non-virtual — that prevents the
mistake at compile time.) `std::unique_ptr<Base>` relies on this too.

## Bug 2: slicing

```cpp
void log(Effect e);   // by value!
Gain g{2.0f};
log(g);               // copies only the Effect part: g is "sliced"; virtual calls see an Effect
```

Pass polymorphic objects by **reference or pointer**, never by value. To prevent slicing by accident,
delete the copy operations of polymorphic bases. If you need to copy a polymorphic object, add a virtual
`clone()`:

{{ex}}

## The NVI idiom (non-virtual interface)

A useful design: the public function is non-virtual and does the common work (checks, logging, locking),
then calls a *private* virtual hook. Derived classes customize the hook but can't skip the checks. The
example's `write()` does this.

!!! tip "Pro tip"
    Enable `-Wnon-virtual-dtor` and `-Wdelete-non-virtual-dtor` (the latter is in `-Wall`). clang-tidy's
    `cppcoreguidelines-slicing` check catches slicing.
""",
files={"": r'''
#include <iostream>
#include <memory>
#include <span>
#include <string>
#include <vector>

class AudioSink {                               // interface + NVI
public:
    virtual ~AudioSink() = default;
    AudioSink(const AudioSink&) = delete;       // prevent slicing copies
    AudioSink& operator=(const AudioSink&) = delete;

    void write(std::span<const float> buf) {     // non-virtual: common checks
        if (buf.empty()) return;
        ++writes_;
        do_write(buf);                           // customization point
    }
    int writes() const { return writes_; }
    virtual std::unique_ptr<AudioSink> clone() const = 0;   // polymorphic copy

protected:
    AudioSink() = default;
private:
    virtual void do_write(std::span<const float> buf) = 0;
    int writes_ = 0;
};

class ConsoleSink final : public AudioSink {
public:
    explicit ConsoleSink(std::string tag) : tag_{std::move(tag)} {}
    std::unique_ptr<AudioSink> clone() const override { return std::make_unique<ConsoleSink>(tag_ + "'"); }
private:
    void do_write(std::span<const float> buf) override {
        std::cout << tag_ << " got " << buf.size() << " samples\n";
    }
    std::string tag_;
};

class Probe {
public:
    virtual ~Probe() { std::cout << "~Probe\n"; }
};
class BigProbe : public Probe {
public:
    ~BigProbe() override { std::cout << "~BigProbe (members freed)\n"; }
    std::vector<int> data = std::vector<int>(1000);
};

int main() {
    std::unique_ptr<AudioSink> sink = std::make_unique<ConsoleSink>("speaker");
    const std::vector<float> buf(256);
    sink->write(buf);
    sink->write({});                             // ignored by the NVI wrapper
    auto copy = sink->clone();
    copy->write(buf);
    std::cout << "writes: " << sink->writes() << ' ' << copy->writes() << '\n';

    std::unique_ptr<Probe> p = std::make_unique<BigProbe>();
    p.reset();                                   // virtual dtor: both destructors run
}
'''},
takeaways=["A pure virtual function makes a class abstract; pure-virtual-only classes are interfaces.",
"Polymorphic bases need a public virtual destructor (or a protected non-virtual one).",
"Passing a derived object by value as a base slices it; pass by reference/pointer and delete base copies.",
"Use `clone()` for polymorphic copies and NVI to keep checks in non-virtual public functions."],
quiz=[("What happens with `Base* p = new Derived; delete p;` if `~Base` isn't virtual?", "Undefined behaviour; in practice only `~Base` runs and the `Derived` part (its members) is never destroyed."),
("What is slicing?", "Copying a derived object into a base-class object, which copies only the base subobject; the derived data and overrides are lost."),
("Why make a polymorphic base's copy constructor deleted?", "To make accidental slicing copies (pass-by-value, assignment to a base object) compile errors.")]),

dict(title="Multiple and virtual inheritance (optional)", std="C++20", minutes=9, area="OOP: inheritance & polymorphism",
features=[("Multiple inheritance", "C++98"), ("The diamond problem, virtual inheritance", "C++98"), ("Pointer adjustment with multiple bases", "—"), ("Mixins / interface-only multiple inheritance", "—")],
why="""
Can a class inherit from two base classes? In C++, yes. It's mostly useful for implementing several
*interfaces* at once — a `MediaPlayer` that is both an `AudioSink` and a `Controllable`, say. This lesson
is marked optional: you'll rarely write complex multiple inheritance, but you'll meet it in frameworks
and you should understand the diamond problem when you see it.
""",
body="""
## Implementing several interfaces

This is the safe, common use: each base is an interface (no data), and the class implements all of them.

## The diamond

If `B` and `C` both inherit from `A`, and `D` inherits from both `B` and `C`, then by default `D` contains
**two** `A` subobjects. `d.a_member` is ambiguous, and converting `D*` to `A*` is ambiguous.

```mermaid
flowchart BT
  B --> A
  C --> A
  D --> B
  D --> C
```

**Virtual inheritance** (`class B : public virtual A`) makes `B` and `C` share a single `A` subobject. The
price: the most-derived class must construct the virtual base directly, layout is more complex, and access
to the virtual base goes through an extra indirection.

{{ex}}

## Pointer adjustment

With multiple bases, converting `Player*` to `Controllable*` may *change the pointer value*: the
`Controllable` subobject lives at an offset inside the `Player`. That's normal and handled by the compiler
— but it's why you must never cast between such pointers with `reinterpret_cast` or through `void*`
without going back to the exact original type.

!!! tip "Practical advice"
    Multiple inheritance of interfaces: fine. Multiple inheritance of classes with state: think twice.
    Virtual inheritance: only when you truly need the shared-base semantics (e.g. `std::iostream`
    inherits virtually from `std::ios_base` via `basic_ios`).
""",
files={"": r'''
#include <iostream>

struct AudioSink { virtual ~AudioSink() = default; virtual void write(int n) = 0; };
struct Controllable { virtual ~Controllable() = default; virtual void pause() = 0; };

class Player : public AudioSink, public Controllable {      // implements two interfaces
public:
    void write(int n) override { std::cout << "write " << n << '\n'; }
    void pause() override { std::cout << "paused\n"; }
};

struct Device { int id = 0; explicit Device(int i) : id{i} {} };
struct Input : virtual Device { Input() : Device{1} {} };
struct Output : virtual Device { Output() : Device{2} {} };
struct Duplex : Input, Output { Duplex() : Device{42} {} };   // most-derived constructs the virtual base

int main() {
    Player p;
    AudioSink* s = &p;
    Controllable* c = &p;
    s->write(128);
    c->pause();
    std::cout << "pointer adjusted? " << std::boolalpha
              << (static_cast<void*>(s) != static_cast<void*>(c)) << '\n';

    Duplex d;
    std::cout << "one shared Device, id=" << d.id << '\n';   // unambiguous thanks to virtual inheritance
}
'''},
takeaways=["Multiple inheritance of interfaces is common and safe.",
"A diamond without virtual inheritance duplicates the shared base; `virtual` inheritance shares it.",
"The most-derived class initializes virtual bases.",
"Converting between base pointers may adjust the address — use `static_cast`/`dynamic_cast`, never `reinterpret_cast`."],
quiz=[("In a non-virtual diamond, how many `A` subobjects does `D` have?", "Two — one via `B` and one via `C`."),
("With virtual inheritance, who calls the virtual base's constructor?", "The most-derived class. Initializers for the virtual base in intermediate classes are ignored when they aren't the most-derived."),
("Why can `static_cast<void*>(s) != static_cast<void*>(c)` be true for the same object?", "The two base subobjects live at different offsets within the derived object.")]),

dict(title="RTTI: typeid, dynamic_cast, and std::any", std="C++20", minutes=9, area="OOP: inheritance & polymorphism",
features=[("`dynamic_cast` (pointers and references)", "C++98"), ("`typeid`, `std::type_info`, `<typeinfo>`", "C++98"), ("`std::type_index`", "C++11"), ("`std::any`", "C++17"), ("`-fno-rtti` and its consequences", "—")],
why="""
Sometimes you hold an `Effect*` and need to know: "is this actually a `Reverb`?" C++ can answer at run time
with RTTI (run-time type information). It's useful, it's occasionally a design smell, and on embedded and
some Android builds it's turned off entirely. Let's see the tools and their trade-offs.
""",
body="""
## `dynamic_cast`

`dynamic_cast<Derived*>(base_ptr)` returns a valid pointer if the object really is a `Derived` (or derived
from it), and `nullptr` otherwise. With references, failure throws `std::bad_cast`. It only works on
polymorphic types (at least one virtual function).

## `typeid`

`typeid(expr)` returns a `const std::type_info&` describing the *dynamic* type for polymorphic glvalues.
`type_info::name()` is implementation-defined (GCC/Clang return a mangled name like `6Reverb`), so use it
for debugging, not for logic. To use types as map keys, wrap them in `std::type_index`.

## `std::any` (C++17)

`std::any` holds a value of *any* copyable type and remembers which one; `std::any_cast<T>` gets it back
(throwing `std::bad_any_cast` on mismatch). It's handy for property bags and plugin metadata, but you lose
compile-time type checking — prefer `std::variant` (Week 9) when the set of types is known.

{{ex}}

## The design smell

```cpp
if (auto* r = dynamic_cast<Reverb*>(e)) r->set_room(0.8f);
else if (auto* g = dynamic_cast<Gain*>(e)) g->set_gain(2.0f);
// ... a growing chain of casts
```

A chain of `dynamic_cast`s usually means a virtual function is missing (`e->apply_preset(p)`), or that
the set of types is closed and a `std::variant` + `std::visit` would be clearer and faster.

## No RTTI builds

Many embedded and game builds compile with `-fno-rtti` (and the Android NDK historically defaulted to it;
modern NDK CMake toolchains enable RTTI and exceptions by default). Without RTTI, `dynamic_cast` on
polymorphic types and `typeid` don't compile, and `std::any` is unavailable with some libraries. Design
libraries so the core doesn't require RTTI.
""",
files={"": r'''
#include <any>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <typeindex>
#include <typeinfo>
#include <vector>

struct Effect { virtual ~Effect() = default; };
struct Gain : Effect { float g = 1.0f; };
struct Reverb : Effect { float room = 0.5f; };

int main() {
    std::vector<std::unique_ptr<Effect>> fx;
    fx.push_back(std::make_unique<Gain>());
    fx.push_back(std::make_unique<Reverb>());

    std::map<std::type_index, std::string> names{{typeid(Gain), "Gain"}, {typeid(Reverb), "Reverb"}};
    for (const auto& e : fx) {
        const Effect& ref = *e;
        std::cout << "dynamic type: " << names[typeid(ref)];
        if (auto* r = dynamic_cast<Reverb*>(e.get())) std::cout << " (room=" << r->room << ')';
        std::cout << '\n';
    }

    try {
        Effect& first = *fx[0];
        auto& r = dynamic_cast<Reverb&>(first);   // it's a Gain: throws
        (void)r;
    } catch (const std::bad_cast&) {
        std::cout << "bad_cast: first effect is not a Reverb\n";
    }

    std::map<std::string, std::any> props{{"rate", 48000}, {"codec", std::string{"opus"}}, {"vbr", true}};
    std::cout << "rate=" << std::any_cast<int>(props["rate"])
              << " codec=" << std::any_cast<std::string>(props["codec"]) << '\n';
    try {
        std::cout << std::any_cast<double>(props["rate"]);
    } catch (const std::bad_any_cast&) {
        std::cout << "bad_any_cast: rate holds an int, not a double\n";
    }
}
'''},
takeaways=["`dynamic_cast` checks the dynamic type: null pointer or `std::bad_cast` on failure.",
"`typeid(...).name()` is implementation-defined; use `std::type_index` as a map key.",
"`std::any` stores any copyable value with runtime type checks; prefer `std::variant` for closed sets.",
"Chains of `dynamic_cast` are a design smell; some builds disable RTTI entirely."],
quiz=[("What does `dynamic_cast<D*>(p)` return if `*p` isn't a `D`?", "`nullptr`. (The reference form throws `std::bad_cast`.)"),
("Why shouldn't program logic depend on `typeid(x).name()`?", "Its contents are implementation-defined (and often mangled); they differ between compilers."),
("When is `std::variant` a better choice than `std::any`?", "When the set of possible types is known at compile time: variant is type-checked, needs no heap allocation, and supports exhaustive `std::visit`.")]),
],
assignment=dict(title="A plugin-style effect chain", task="""
Design an `Effect` interface (NVI: public non-virtual `process(std::span<float>)` that skips disabled effects;
private virtual `do_process`). Implement `Gain`, `Clip` and `Delay` (a simple fixed delay line).

1. Store effects in `std::vector<std::unique_ptr<Effect>>`.
2. Support `clone()` so a chain can be duplicated.
3. Process an impulse `[1, 0, 0, 0, 0, 0]` through the chain and print the result.
4. No `dynamic_cast` allowed.
""", solution=r'''
#include <iostream>
#include <memory>
#include <span>
#include <vector>

class Effect {
public:
    virtual ~Effect() = default;
    void process(std::span<float> buf) { if (enabled_) do_process(buf); }
    void set_enabled(bool e) { enabled_ = e; }
    virtual std::unique_ptr<Effect> clone() const = 0;
protected:
    Effect() = default;
    Effect(const Effect&) = default;            // usable by clone() in derived classes only
    Effect& operator=(const Effect&) = delete;
private:
    virtual void do_process(std::span<float> buf) = 0;
    bool enabled_ = true;
};

class Gain final : public Effect {
public:
    explicit Gain(float g) : g_{g} {}
    std::unique_ptr<Effect> clone() const override { return std::make_unique<Gain>(*this); }
private:
    void do_process(std::span<float> b) override { for (auto& x : b) x *= g_; }
    float g_;
};

class Clip final : public Effect {
public:
    std::unique_ptr<Effect> clone() const override { return std::make_unique<Clip>(*this); }
private:
    void do_process(std::span<float> b) override { for (auto& x : b) x = x > 1 ? 1 : (x < -1 ? -1 : x); }
};

class Delay final : public Effect {
public:
    Delay(std::size_t samples, float mix) : line_(samples), mix_{mix} {}
    std::unique_ptr<Effect> clone() const override { return std::make_unique<Delay>(*this); }
private:
    void do_process(std::span<float> b) override {
        for (auto& x : b) {
            const float delayed = line_[pos_];
            line_[pos_] = x;
            pos_ = (pos_ + 1) % line_.size();
            x += mix_ * delayed;
        }
    }
    std::vector<float> line_;
    std::size_t pos_ = 0;
    float mix_;
};

using Chain = std::vector<std::unique_ptr<Effect>>;

Chain clone_chain(const Chain& c) {
    Chain out;
    for (const auto& e : c) out.push_back(e->clone());
    return out;
}

void run(Chain& chain, const char* label) {
    std::vector<float> buf{1, 0, 0, 0, 0, 0};
    for (auto& e : chain) e->process(buf);
    std::cout << label << ": ";
    for (float x : buf) std::cout << x << ' ';
    std::cout << '\n';
}

int main() {
    Chain chain;
    chain.push_back(std::make_unique<Gain>(3.0f));
    chain.push_back(std::make_unique<Delay>(2, 0.5f));
    chain.push_back(std::make_unique<Clip>());
    Chain copy = clone_chain(chain);
    run(chain, "original");
    copy[2]->set_enabled(false);
    run(copy, "copy, clip off");
}
'''))
