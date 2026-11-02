# Lesson 15.2: Linking, the ODR, ABI, and extern "C"

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

"undefined reference to `mixer::Gain::apply(double)`" — every C++ programmer meets the linker the hard way.
Understanding what the compiler hands to the linker explains these errors, the One Definition Rule, why C
libraries need `extern "C"`, and why changing a private member can break binaries that use your library.

## The two phases

The compiler turns each `.cpp` (translation unit) into an object file with **symbols** — defined and
referenced names. The linker matches references to definitions. "Undefined reference" = nobody defined it
(missing `.cpp` or library in the link); "multiple definition" = two TUs defined it.

## The One Definition Rule

Each non-inline function or variable must be defined exactly once in the program. Things defined in
headers (classes, templates, `inline` functions, C++17 `inline` variables) may appear in many TUs *but must
be token-identical*. Two different `struct Config` definitions with the same name in two TUs is an ODR
violation — undefined behaviour, often silent.

Give helpers **internal linkage** (anonymous namespace or `static`) so they can't collide.

## Name mangling and `extern "C"`

C++ encodes parameter types into symbol names (`_ZN5mixer4Gain5applyEd`) to support overloading. C doesn't.
To call C code from C++, or expose a C API from C++, use `extern "C"` — no overloading, no mangling.

```cpp title="examples/week15/lesson02.cpp"
--8<-- "examples/week15/lesson02.cpp"
```

**Output**:

```text
--8<-- "examples/week15/lesson02.out"
```

## ABI

The **ABI** is the binary contract: object layout, calling conventions, mangling, vtable layout. Adding a
private data member changes `sizeof` and breaks every binary compiled against the old header. Libraries that
need stability use the **pimpl** idiom (Week 5) or a C API. (GCC's switch to a C++11-conforming
`std::string` in 2015 required a dual ABI — that's how costly ABI breaks are.)

## Key takeaways

!!! success "Key takeaways"
    - Undefined reference = missing definition in the link; multiple definition = defined twice.
    - The ODR requires identical definitions across TUs; violations are silent UB.
    - Use anonymous namespaces for TU-local helpers and `inline` for header definitions.
    - `extern "C"` disables mangling for C interop; pimpl or C APIs preserve ABI stability.

## Quiz

**Q1.** Why can't C code call an overloaded C++ function directly?

??? question "Show answer"
    C++ mangles parameter types into symbol names; C expects plain names. Use `extern "C"` wrappers (which can't be overloaded).

**Q2.** Is adding a private member to a class in a shared library's header ABI-compatible?

??? question "Show answer"
    No — it changes the object's size/layout, breaking binaries compiled against the old header.

**Q3.** How do you define a global constant in a header without ODR problems?

??? question "Show answer"
    `inline constexpr` (C++17 inline variable) — or `constexpr` at namespace scope, which has internal linkage.

