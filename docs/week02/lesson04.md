# Lesson 2.4: Scope, lifetime, storage duration and namespaces

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

Every bug involving a dangling pointer or a use-after-free comes down to one question: *when does this
object die?* In garbage-collected languages you rarely ask it. In C++ you get to decide — which is where
the performance (and the deterministic cleanup!) comes from. This lesson gives you the rules.

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

```cpp title="examples/week02/lesson04.cpp"
--8<-- "examples/week02/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week02/lesson04.out"
```

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

## Key takeaways

!!! success "Key takeaways"
    - Scope is about names; lifetime is about objects.
    - Automatic objects die at the end of their block, in reverse order of construction.
    - Function-local statics are initialized on first use, thread-safely (C++11).
    - Never put `using namespace` in a header; use nested namespaces `a::b` (C++17).

## Quiz

**Q1.** In what order are three local objects `a`, `b`, `c` destroyed?

??? question "Show answer"
    `c`, `b`, `a` — reverse order of construction.

**Q2.** What is the static initialization order fiasco and one fix?

??? question "Show answer"
    Globals in different translation units are initialized in unspecified order, so one global's constructor may use another before it's initialized. Fix: replace the global with a function returning a reference to a function-local static (construct on first use), or use `constinit`/`constexpr` for constant initialization.

**Q3.** Why is `using namespace std;` in a header bad?

??? question "Show answer"
    Every file including the header gets all of `std` dumped into the global namespace, which can cause ambiguities and silently change overload resolution.

