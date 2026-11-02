WEEK = dict(num=1, title="Getting started: toolchain, compilation, types", intro="""
Welcome to Week 1! This week is about getting comfortable. We'll install a compiler, write a program,
and then — this is the part most courses skip — understand what actually happens between your `.cpp`
file and a running program. Then we'll meet C++'s basic types, how variables get initialized, and the
operators you'll use every day.

If you already write some C++, don't skip the compilation-model lesson. Many "mysterious" linker errors
you've seen in Android NDK builds will suddenly make sense.
""", lessons=[
dict(title="Hello, toolchain: compilers, CMake and Compiler Explorer", std="C++20", minutes=10, area="Basics: toolchain & compilation",
features=[("g++ / clang++ command line, warnings flags", "—"), ("CMake basics (project, add_executable, target_compile_features)", "—"), ("Compiler Explorer (godbolt.org)", "—"), ("`main`, return codes, `std::cout`", "C++98")],
why="""
Before we can learn a language, we need a way to *run* it. In Python you type `python file.py` and
you're done. C++ is different: it is a **compiled** language, so a tool called a *compiler* turns your
text into machine code ahead of time. That's a big part of why C++ is fast — and also why there are a
few more moving parts. Let's set those up once, properly, so they never get in your way again.
""",
body="""
## Your first program

Let's start with the smallest useful C++ program.

{{ex}}

Let's go through it line by line:

- `#include <iostream>` pulls in the declarations for input/output streams. (We'll see exactly what
  "pulls in" means in the next lesson.)
- `int main()` is where every hosted C++ program starts. It returns an `int` to the operating system:
  `0` means success.
- `std::cout << "..."` writes text to standard output. `std::` means "from the standard library namespace".
- `'\\n'` is a newline character.

## Compiling it by hand

On Linux or macOS, with GCC or Clang installed:

```bash
g++ -std=c++20 -Wall -Wextra -Wpedantic hello.cpp -o hello
./hello
```

Each flag matters:

| Flag | What it does |
|---|---|
| `-std=c++20` | Which version of the language to use. C++ evolves every 3 years: 11, 14, 17, 20, 23, 26. |
| `-Wall -Wextra` | Turn on lots of useful warnings. Despite the name, `-Wall` is *not* all of them. |
| `-Wpedantic` | Warn about non-standard compiler extensions. |
| `-o hello` | Name the output file. |

!!! tip "Pro tip: treat warnings as bugs"
    A warning is the compiler saying "this is legal, but you probably didn't mean it."
    In this course every example compiles **warning-free** with these flags; that's checked
    automatically. On real projects, add `-Werror` in CI so warnings can't creep in.

`clang++` accepts the same flags. On Windows, MSVC uses `/std:c++20 /W4`. Throughout the course
we test with both GCC and Clang.

## Compiler Explorer: your new best friend

[Compiler Explorer](https://godbolt.org) lets you paste code and instantly see the assembly produced by
dozens of compilers. You don't need to read assembly fluently. But when we talk about "zero-cost
abstractions" later, you'll be able to *see* that the abstraction really did disappear. Bookmark it.

## CMake: building more than one file

For anything beyond one file, you'll want a build system. The de-facto standard is **CMake**. A minimal
`CMakeLists.txt` looks like this:

```cmake
cmake_minimum_required(VERSION 3.20)
project(hello LANGUAGES CXX)

add_executable(hello hello.cpp)
target_compile_features(hello PRIVATE cxx_std_20)
target_compile_options(hello PRIVATE -Wall -Wextra -Wpedantic)
```

And you build it with:

```bash
cmake -S . -B build        # configure: generate build files into ./build
cmake --build build        # build
./build/hello
```

Notice the pattern: **targets** (here `hello`) and properties attached to targets. That's "modern CMake",
and we'll go much deeper in Week 15. Coming from Android? Good news: the NDK uses exactly this
CMake, so this skill transfers directly.

## A slightly bigger example

Here's a program that reads from the user. Don't worry about every detail yet.

{{ex:_input}}

When there's no input (as in our automated test run), `std::cin >> name` fails, and we fall back
to a default. Checking whether input succeeded is a habit worth building on day one.
""",
files={"": r'''
#include <iostream>

int main() {
    std::cout << "Hello, C++!\n";
    return 0;  // 0 tells the OS "success"; you may omit this line in main only
}
''', "_input": r'''
#include <iostream>
#include <string>

int main() {
    std::cout << "What's your name? ";
    std::string name;
    if (!(std::cin >> name)) {   // reading can fail (e.g. end of input)
        name = "friend";
    }
    std::cout << "\nNice to meet you, " << name << "!\n";
}
'''},
takeaways=["C++ is compiled ahead of time; the compiler turns source text into a native executable.",
"Always compile with a fixed standard and warnings on: `-std=c++20 -Wall -Wextra -Wpedantic`.",
"Compiler Explorer shows you what the compiler generates — use it to build intuition.",
"CMake describes *targets* and their properties; the NDK uses the same CMake."],
quiz=[("What does `return 0;` from `main` mean?", "It reports success to the operating system. Non-zero means failure. In `main` (and only `main`) you may omit it, and it behaves as `return 0;`."),
("Does `-Wall` enable all warnings?", "No. Despite its name it enables a common set. `-Wextra` adds more, and there are still others (like `-Wconversion`) that you turn on separately."),
("In CMake, what is a *target*?", "Something the build produces (an executable or library) that properties like compile features, options and include paths are attached to, e.g. `add_executable(hello ...)` creates target `hello`.")],
lab=dict(task="""
Write a program that asks for two integers and prints their sum and product. If reading fails,
print `invalid input` and return `1`. Build it once by hand with `g++` and once with CMake.
""", starter=r'''
#include <iostream>

int main() {
    int a = 0, b = 0;
    // TODO: read a and b; on failure print "invalid input" and return 1
    std::cout << "sum=" << a + b << '\n';
}
''', solution={"run": False, "code": r'''
#include <iostream>

int main() {
    int a = 0, b = 0;
    if (!(std::cin >> a >> b)) {
        std::cout << "invalid input\n";
        return 1;
    }
    std::cout << "sum=" << a + b << " product=" << a * b << '\n';
}
'''})),

dict(title="The compilation model: preprocessor, translation units, linking, ODR", std="C++20", minutes=12, area="Basics: toolchain & compilation",
features=[("Preprocessor: #include, #define, #if, include guards, #pragma once", "C++98"), ("Translation units, declarations vs definitions", "C++98"), ("Linking, undefined reference errors", "—"), ("One Definition Rule (ODR), `inline` variables", "C++17"), ("Headers vs source files, `static`/anonymous namespaces (internal linkage)", "C++98")],
why="""
Here's a problem you've probably hit: your code compiles, but then the build fails with
`undefined reference to 'foo()'`. Or the opposite: `multiple definition of 'foo'`. These errors aren't
from the compiler at all — they're from the *linker*. Understanding the three stages of a build makes these
errors go from mysterious to obvious. Let's see how this works.
""",
body="""
## Three stages

When you run `g++ main.cpp util.cpp -o app`, three things happen:

```mermaid
flowchart LR
  A[main.cpp] -->|preprocess| B[translation unit]
  B -->|compile| C[main.o]
  D[util.cpp] -->|preprocess| E[translation unit]
  E -->|compile| F[util.o]
  C --> L{link}
  F --> L
  L --> G[app]
```

1. **Preprocessing.** Text substitution. `#include "util.h"` literally pastes the contents of `util.h`
   in place. `#define` and `#if` are also handled here. The result is a **translation unit** (TU).
2. **Compilation.** Each TU is compiled *independently* into an object file (`.o`). The compiler
   only knows what it can see in that one TU.
3. **Linking.** The linker stitches object files and libraries together, matching each *use* of a
   function with its single *definition*.

That word "independently" is the key to everything. When compiling `main.cpp`, the compiler has never
seen `util.cpp`. So how can `main` call a function defined there? Through a **declaration**.

## Declarations vs definitions

- A *declaration* says "this thing exists, and here is its type": `int add(int, int);`
- A *definition* provides the thing itself: `int add(int a, int b) { return a + b; }`

You can declare something many times, but (for most things) define it exactly once in the whole program.
That's the **One Definition Rule (ODR)**.

So the classic layout is: declarations in a header (`util.h`), definitions in a source file (`util.cpp`),
and every file that needs them includes the header.

```cpp
// util.h
#pragma once            // include guard: paste this file at most once per TU
int add(int a, int b);  // declaration only

// util.cpp
#include "util.h"
int add(int a, int b) { return a + b; }  // the one definition

// main.cpp
#include "util.h"
int main() { return add(2, 3); }
```

Now the two classic errors become easy to explain:

- **`undefined reference to add(int, int)`**: you declared it, used it, but the linker never got an
  object file containing the definition. (Forgot to compile/link `util.cpp`, or the signatures differ.)
- **`multiple definition of add`**: you put the *definition* in the header, and two `.cpp` files included
  it. Now two object files both define `add`.

## The wrong way, then the fix

Putting a definition in a header is the most common mistake:

```cpp
// config.h  -- WRONG if included from two .cpp files
int max_users = 100;          // a definition! each TU gets its own -> link error
```

There are two good fixes. The C++17 way is an **inline variable**: `inline` tells the linker "there may be
identical copies in many TUs; keep one".

```cpp
// config.h  -- OK
inline int max_users = 100;          // C++17 inline variable
constexpr int max_sessions = 8;      // constexpr at namespace scope: internal linkage, also fine
```

Functions defined in headers need `inline` for the same reason (member functions defined inside a class
body and templates are implicitly OK).

## Internal linkage: keeping helpers private

Sometimes a helper should be visible only inside one `.cpp` file. Put it in an **anonymous namespace**
(or mark it `static`). It then has *internal linkage*: two files can each have their own `helper()` with
no conflict.

Here's a single-file program that demonstrates these ideas — we can't show multiple files in one
example, but we can show the declaration/definition split and internal linkage:

{{ex}}

## The preprocessor: useful, but keep it small

The preprocessor knows nothing about C++ — it's text substitution. That's exactly why macros are
risky. The classic bug:

```cpp
#define SQUARE(x) x * x
int y = SQUARE(1 + 2);   // expands to 1 + 2 * 1 + 2 == 5, not 9!
```

In modern C++, use `constexpr` functions instead of function-like macros. Keep the preprocessor for
`#include`, include guards, and conditional compilation (`#if defined(__ANDROID__)`), which is still
genuinely useful.

!!! warning "Common pitfall: ODR violations that *don't* error"
    If two TUs define the *same inline function or class* differently (say, different `#define`s
    changed a struct's layout), the linker usually picks one silently. That's undefined behaviour and
    a nightmare to debug. Keep headers self-contained and avoid configuration macros that change
    layouts. In C++20, **modules** (Week 15) fix much of this.
""",
files={"": r'''
#include <iostream>

// A declaration: tells the compiler the function exists.
int add(int a, int b);

namespace {                 // anonymous namespace => internal linkage
int helper(int x) { return x * 10; }
}

inline int global_counter = 0;   // C++17 inline variable: safe to put in a header

constexpr int square(int x) { return x * x; }  // instead of #define SQUARE(x)

int main() {
    ++global_counter;
    std::cout << add(2, 3) << ' ' << helper(4) << ' ' << square(1 + 2)
              << ' ' << global_counter << '\n';
}

// The definition can come later in the file (or in another file entirely).
int add(int a, int b) { return a + b; }
'''},
takeaways=["Build = preprocess → compile each translation unit independently → link.",
"Headers hold declarations; one `.cpp` holds each definition (the ODR).",
"`undefined reference` = missing definition at link time; `multiple definition` = defined in a header without `inline`.",
"Use `inline` (C++17) variables / functions or `constexpr` for things defined in headers.",
"Prefer `constexpr` functions over function-like macros."],
quiz=[("You get `undefined reference to 'foo()'`. Is this a compiler or linker error, and what are two likely causes?", "A linker error. Either the `.cpp` defining `foo` wasn't compiled/linked into the program, or the declaration and definition don't match (different parameter types, namespace, or `extern \"C\"` mismatch)."),
("Why does `int x = 5;` in a header cause trouble, but `inline int x = 5;` doesn't?", "Each TU that includes the header gets its own definition of `x`, violating the ODR (multiple definitions at link time). `inline` allows identical definitions in multiple TUs; the linker merges them."),
("What does `SQUARE(1+2)` evaluate to with `#define SQUARE(x) x * x`?", "5, because it expands textually to `1 + 2 * 1 + 2`. Use a `constexpr` function instead."),
("What does an anonymous namespace do?", "Gives everything inside it internal linkage, so it is private to that translation unit and can't clash with names in other files.")]),

dict(title="Fundamental types, literals, and fixed-width integers", std="C++20", minutes=11, area="Basics: types & values",
features=[("Fundamental types: bool, char, int, long, long long, float, double", "C++98"), ("Integer literals: hex, octal, binary `0b`, digit separators `'`", "C++14"), ("`<cstdint>`: int32_t, uint8_t, size_t...", "C++11"), ("`<limits>`: std::numeric_limits", "C++98"), ("`char8_t`, `char16_t`, `char32_t`", "C++20"), ("`sizeof`, `alignof`", "C++11"), ("`nullptr`", "C++11"), ("Floating point basics and precision", "C++98")],
why="""
Suppose you're decoding an audio stream: 16-bit signed samples, a 32-bit sample-rate field, an 8-bit
channel count. If you pick `int` for everything and the code runs on a platform where `int` isn't the
size you assumed, the file is garbage. C++ gives you precise control over representation — but you
have to know what the types actually guarantee. Let's look.
""",
body="""
## The basic types

| Type | Typical size (64-bit Linux/Android) | Guaranteed by the standard |
|---|---|---|
| `bool` | 1 byte | holds `true`/`false` |
| `char` | 1 byte | `sizeof(char) == 1`; signedness is implementation-defined! |
| `short` | 2 | at least 16 bits |
| `int` | 4 | at least 16 bits |
| `long` | 8 (4 on Windows) | at least 32 bits |
| `long long` | 8 | at least 64 bits |
| `float` / `double` | 4 / 8 | usually IEEE-754 single/double |

Notice "at least". The standard deliberately leaves exact sizes to the platform. On Windows, `long` is
32 bits; on 64-bit Linux it's 64. That has broken plenty of portable code.

## When size matters, say so: `<cstdint>`

For file formats, network protocols and hardware registers, use the fixed-width types:
`std::int8_t`, `std::uint16_t`, `std::int32_t`, `std::uint64_t`. For sizes and indexes use
`std::size_t` (what `sizeof` and `.size()` return).

{{ex}}

A few things to notice in that output:

- `std::numeric_limits<T>` (from `<limits>`) tells you a type's range, precision and more at compile time.
- `0.1 + 0.2` is not exactly `0.3`. Floating point stores binary fractions; `0.1` has no exact binary
  representation. Never compare floats with `==` unless you know why it's safe.
- `uint8_t` printed via `std::cout` shows up as a *character* because it's (usually) a typedef for
  `unsigned char`. Cast to `int` to print the number. This one bites every multimedia developer at least once.

## Literals

Literals are how you write values in code:

```cpp
int dec = 255, hex = 0xFF, oct = 0377, bin = 0b1111'1111;  // all 255; ' is a digit separator (C++14)
unsigned u = 42u;  long l = 42L;  long long ll = 42LL;  std::size_t n = 42uz; // uz: C++23
double d = 1.5e3;  float f = 1.5f;
char c = 'A';  char8_t c8 = u8'A';  char16_t c16 = u'A';  char32_t c32 = U'A';
const char* s = "text";  bool b = true;  int* p = nullptr;   // nullptr: C++11
```

`nullptr` (C++11) replaced the old `NULL`/`0` for null pointers — it has its own type, so overloads can't
mistake it for an integer.

## Common mistake: assuming `char` is signed

```cpp
char c = '\\xFF';
if (c < 0) { /* true on x86 Linux, FALSE on ARM Linux/Android! */ }
```

On x86, plain `char` is signed; on ARM (most Android devices), it's unsigned. If you mean "a byte", use
`unsigned char`, `std::uint8_t`, or `std::byte` (Week 3).

!!! tip "Pro tip"
    `static_assert(sizeof(Header) == 12);` (Week 9) lets you lock down assumptions about layout at compile
    time, so a port to a new platform fails loudly instead of silently corrupting data.
""",
files={"": r'''
#include <cstdint>
#include <iostream>
#include <limits>

int main() {
    std::cout << "sizeof(int)=" << sizeof(int)
              << " sizeof(long long)=" << sizeof(long long)
              << " sizeof(double)=" << sizeof(double) << '\n';

    std::cout << "int range: " << std::numeric_limits<int>::min() << " .. "
              << std::numeric_limits<int>::max() << '\n';
    std::cout << "uint16_t max: " << std::numeric_limits<std::uint16_t>::max() << '\n';

    int bin = 0b1111'1111;  // binary literal with digit separator
    std::cout << "0b1111'1111 = " << bin << ", 0xFF = " << 0xFF << '\n';

    double x = 0.1 + 0.2;
    std::cout << std::boolalpha << "0.1 + 0.2 == 0.3 ? " << (x == 0.3) << '\n';
    std::cout.precision(17);
    std::cout << "0.1 + 0.2 = " << x << '\n';

    std::uint8_t channels = 65;
    std::cout << "uint8_t printed directly: " << channels
              << ", as int: " << static_cast<int>(channels) << '\n';
}
'''},
takeaways=["The standard guarantees minimum sizes, not exact ones; `long` differs between Windows and Linux.",
"Use `<cstdint>` fixed-width types for formats/protocols, `std::size_t` for sizes.",
"Floating point is approximate: don't compare with `==` casually.",
"Plain `char` signedness differs between x86 and ARM; use `unsigned char`/`std::byte` for bytes.",
"`uint8_t` prints as a character with iostreams; cast to `int`."],
quiz=[("Is `sizeof(long)` always 8 on 64-bit systems?", "No. It's 8 on 64-bit Linux/macOS/Android (LP64) but 4 on 64-bit Windows (LLP64)."),
("Why does `std::cout << std::uint8_t{65}` print `A`?", "`std::uint8_t` is typically an alias for `unsigned char`, and the stream prints character types as characters. Cast to `int` first, or use `std::format`/`std::print` (Week 12), which format `unsigned char` as a number."),
("What's the value of `0b1010'0000`?", "160 (binary 10100000). The `'` is just a digit separator."),
("Why prefer `nullptr` over `NULL`?", "`nullptr` has type `std::nullptr_t` and converts only to pointer types, so overload resolution can't confuse it with an integer like `NULL` (often `0`) could.")]),

dict(title="Variables and initialization: auto, const, constexpr", std="C++20", minutes=10, area="Basics: types & values",
features=[("Variable initialization forms: `=`, `()`, `{}`", "C++11"), ("Brace initialization prevents narrowing", "C++11"), ("`auto` type deduction", "C++11"), ("`const`", "C++98"), ("`constexpr` variables", "C++11"), ("`decltype`", "C++11"), ("Uninitialized variables (indeterminate values)", "C++98")],
why="""
Here's a bug that has shipped in real products: `int volume; if (muted) volume = 0; play(volume);`. When
not muted, `volume` is *uninitialized* — reading it is undefined behaviour. C++ won't stop you, so you
need habits that make the mistake impossible. This lesson is about those habits.
""",
body="""
## Always initialize

A local variable of fundamental type without an initializer has an *indeterminate* value. Reading it is
undefined behaviour (UB) — the program may print garbage, or the optimizer may do something truly strange.

```cpp
int x;            // WRONG (if you read it before assigning)
int y = 0;        // OK
```

## Three ways to initialize (and which to prefer)

```cpp
int a = 3;      // copy-initialization
int b(3);       // direct-initialization
int c{3};       // list-initialization (brace init), C++11
```

All three give 3 here. The braces have one superpower: **they reject narrowing conversions**.

```cpp
double ratio = 2.7;
int n1 = ratio;   // compiles, silently truncates to 2 (warning with -Wconversion)
int n2{ratio};    // ERROR: narrowing conversion from double to int
```

That's why many style guides say "prefer `{}`". There are a few pitfalls with braces and constructors
that take `std::initializer_list` (we'll meet them in Week 4), but for plain variables, braces are a great
default.

## `auto`: let the compiler figure out the type

`auto` deduces the type from the initializer:

```cpp
auto count = 10;        // int
auto ratio = 0.5;       // double
auto name = std::string{"Ada"};  // std::string
```

Use `auto` when the type is obvious from the right-hand side or long and noisy (iterators). It also
*forces* you to initialize — `auto x;` doesn't compile. One gotcha: `auto` drops top-level `const` and
references; we'll see that in Lesson 2.3.

## `const` and `constexpr`

- `const` means "I won't modify this after initialization." The value may be computed at run time.
- `constexpr` means "this is known at compile time" — the compiler must be able to evaluate it.

{{ex}}

`constexpr` values can be used where the language needs a compile-time constant, like array sizes and
template arguments. We'll go much deeper (constexpr functions, `consteval`, `constinit`) in Week 8.

!!! tip "Pro tip: make const the default"
    Mark everything `const` that doesn't need to change. It documents intent, prevents accidents, and
    makes code easier to reason about. Many experienced C++ programmers find most of their local
    variables end up `const`.

## `decltype`: the type of an expression

`decltype(expr)` gives you the declared type of an expression without evaluating it. You'll mostly see it
in generic code, e.g. `decltype(a + b)`. Don't worry about it much yet.
""",
files={"": r'''
#include <iostream>
#include <string>

constexpr int kSampleRate = 48'000;          // compile-time constant
constexpr int kFrameMs = 20;
constexpr int kSamplesPerFrame = kSampleRate * kFrameMs / 1000;

int main() {
    int buffer[kSamplesPerFrame]{};          // OK: size is a constant expression; {} zero-fills
    const auto user = std::string{"Arun"};   // const: computed at runtime, never modified
    auto volume = 0.8;                       // double
    int level{static_cast<int>(volume * 10)};  // explicit conversion; {} would reject implicit narrowing

    decltype(level) copy = level;            // int
    std::cout << user << ": " << kSamplesPerFrame << " samples/frame, level "
              << copy << ", buffer[0]=" << buffer[0] << '\n';
}
'''},
takeaways=["Always initialize variables; reading an uninitialized `int` is undefined behaviour.",
"Brace initialization `{}` rejects narrowing conversions.",
"`auto` deduces from the initializer and forces you to initialize.",
"`const` = won't change; `constexpr` = known at compile time."],
quiz=[("Does `int n{3.5};` compile?", "No. List-initialization forbids narrowing from `double` to `int`. `int n = 3.5;` compiles (truncating to 3), typically with a warning under `-Wconversion`."),
("What's the difference between `const int a = f();` and `constexpr int b = f();`?", "`a` can be initialized at run time; it just can't be modified afterwards. `b` requires `f()` to be evaluable at compile time (a `constexpr` function with constant arguments), otherwise it's a compile error."),
("What type is `auto x = 5u;`?", "`unsigned int`.")]),

dict(title="Operators, integer promotion and narrowing", std="C++20", minutes=11, area="Basics: types & values",
features=[("Arithmetic, comparison, logical operators; precedence", "C++98"), ("Integer promotion and usual arithmetic conversions", "C++98"), ("Signed/unsigned comparison pitfalls; `std::cmp_less` etc.", "C++20"), ("Signed overflow is UB; unsigned wraps", "C++98"), ("`static_cast` and other named casts", "C++98"), ("Order of evaluation rules (C++17 changes)", "C++17")],
why="""
Quick puzzle: what does this print?

```cpp
std::vector<int> v;   // empty
if (-1 < v.size()) std::cout << "less"; else std::cout << "not less";
```

It prints **not less**. `-1` gets converted to an unsigned 64-bit number (a huge value) before the comparison.
This lesson explains the conversion rules that cause surprises like this, and the modern tools to avoid them.
""",
body="""
## The everyday operators

You know most of these from other languages: `+ - * / %`, comparisons `== != < <= > >=`, logical
`&& || !`, assignment `= += -=` and friends, increment `++`/`--`. Two C++-specific notes:

- Integer division truncates toward zero: `-7 / 2 == -3`, and `-7 % 2 == -1`.
- `&&` and `||` short-circuit: in `p && p->ok()`, the right side isn't evaluated if `p` is null.

When precedence isn't obvious, add parentheses. Nobody remembers that `&` binds weaker than `==`.

## Integer promotion: small types become `int`

Before arithmetic, types smaller than `int` (`char`, `short`, `uint8_t`, `bool`) are *promoted* to `int`.
So `uint8_t a = 200, b = 100; auto c = a + b;` gives `c == 300` with type `int` — no overflow.

## Usual arithmetic conversions: the signed/unsigned trap

When you mix two different types, they're converted to a common type. The surprising rule: if one operand
is unsigned and at least as wide as the other, the **signed one is converted to unsigned**. That's the
`-1 < v.size()` puzzle: `-1` becomes `18446744073709551615`.

The fix, in C++20: `std::cmp_less`, `std::cmp_greater` etc. from `<utility>` compare integers *by value*,
regardless of signedness. Or just keep your types consistent (use `std::ssize(v)` for a signed size).

{{ex}}

## Overflow: signed is UB, unsigned wraps

Unsigned arithmetic wraps around modulo 2ⁿ — that's well-defined. **Signed overflow is undefined
behaviour.** The optimizer is allowed to assume it never happens, which can delete your "overflow checks":

```cpp
bool will_overflow(int x) { return x + 1 < x; }   // WRONG: compiler may fold this to `false`
```

Check *before* the operation instead: `x == std::numeric_limits<int>::max()`, or use compiler builtins like
`__builtin_add_overflow` (GCC/Clang) — and in C++26, `<stdckdint.h>`'s `ckd_add` is coming from C23.

## Casts: say what you mean

C++ has named casts so each one is searchable and limited:

| Cast | Use for |
|---|---|
| `static_cast<T>(x)` | Normal, checked-at-compile-time conversions (`double`→`int`, base→derived pointers you know are right) |
| `const_cast<T>(x)` | Removing `const` (rarely legitimate) |
| `reinterpret_cast<T>(x)` | Reinterpreting bits/pointers (low-level, dangerous) |
| `dynamic_cast<T>(x)` | Checked downcasts in class hierarchies (Week 6) |

Avoid C-style `(int)x` casts — they silently pick the most dangerous cast that works.

## Order of evaluation

In `f(a(), b())`, the order in which `a()` and `b()` run is unspecified. C++17 *did* fix some cases:
in `a << b`, `a = b`, `a[b]` and `a.b`, the left side is now evaluated first. So `std::cout << i++ << i;`
is defined since C++17 (but still confusing — don't write it).

!!! warning "Common pitfall"
    Turn on `-Wconversion -Wsign-conversion` for code that does a lot of arithmetic (DSP, codecs).
    They are noisy at first, but they catch exactly the bugs in this lesson.
""",
files={"": r'''
#include <cstdint>
#include <iostream>
#include <utility>
#include <vector>

int main() {
    std::vector<int> v;  // size() == 0, type std::size_t (unsigned)

    // The trap: -1 is converted to a huge unsigned value.
    // (We cast explicitly here so the example compiles warning-free; the implicit
    //  comparison `-1 < v.size()` would trigger -Wsign-compare.)
    std::cout << std::boolalpha;
    std::cout << "-1 < v.size() (as unsigned): " << (static_cast<std::size_t>(-1) < v.size()) << '\n';
    std::cout << "std::cmp_less(-1, v.size()): " << std::cmp_less(-1, v.size()) << '\n';

    std::uint8_t a = 200, b = 100;
    auto c = a + b;  // promoted to int
    std::cout << "200 + 100 with uint8_t operands = " << c << '\n';

    unsigned int u = 0;
    --u;  // well-defined wrap-around
    std::cout << "0u - 1 = " << u << '\n';

    std::cout << "-7 / 2 = " << -7 / 2 << ", -7 % 2 = " << -7 % 2 << '\n';
    double avg = 7.9;
    std::cout << "static_cast<int>(7.9) = " << static_cast<int>(avg) << '\n';
}
'''},
takeaways=["Small integer types are promoted to `int` before arithmetic.",
"Mixing signed and unsigned converts the signed value to unsigned — use `std::cmp_less` & co. (C++20).",
"Signed overflow is UB (the optimizer exploits it); unsigned wraps.",
"Use named casts (`static_cast`), never C-style casts.",
"C++17 fixed evaluation order for `<<`, `=`, `[]`, but function-argument order is still unspecified."],
quiz=[("Why is `x + 1 < x` a bad overflow check for `int x`?", "Signed overflow is undefined behaviour, so the compiler may assume it never happens and simplify the expression to `false`. Check against `INT_MAX` before adding instead."),
("What type and value does `std::uint8_t{250} + std::uint8_t{10}` have?", "`int` with value 260, because of integer promotion."),
("What does `std::cmp_less(-1, 0u)` return?", "`true`. It compares mathematical values regardless of signedness."),
("Which cast would you use to convert a `double` to an `int` deliberately?", "`static_cast<int>(d)`.")],
lab=dict(task="""
Write `int clamp_add(int a, int b)` that returns `a + b`, but saturates at `INT_MAX`/`INT_MIN` instead of
overflowing — without ever performing an overflowing signed addition.
""", solution=r'''
#include <iostream>
#include <limits>

int clamp_add(int a, int b) {
    constexpr int hi = std::numeric_limits<int>::max();
    constexpr int lo = std::numeric_limits<int>::min();
    if (b > 0 && a > hi - b) return hi;   // a + b would exceed hi
    if (b < 0 && a < lo - b) return lo;   // a + b would go below lo
    return a + b;
}

int main() {
    std::cout << clamp_add(2, 3) << ' '
              << clamp_add(std::numeric_limits<int>::max(), 1) << ' '
              << clamp_add(std::numeric_limits<int>::min(), -5) << '\n';
}
''')),
],
assignment=dict(title="A WAV header inspector", task="""
Let's put the week together. A WAV file starts with a 44-byte header. You'll write a program that builds a
header for given parameters into a byte array and then *parses it back*, printing the fields.

Requirements:

1. Use fixed-width types (`std::uint16_t`, `std::uint32_t`) for every field.
2. Write little-endian values byte-by-byte with shifts (don't `memcpy` structs — padding and endianness
   make that non-portable).
3. Compute `byte_rate = sample_rate * channels * bits/8` using `constexpr` where possible.
4. Compile warning-free with `-Wall -Wextra -Wpedantic`.

Don't worry if the shifting feels unfamiliar: we cover bit operations properly in Week 3. Peek at the
solution if you get stuck — that's part of learning.
""", starter=r'''
#include <array>
#include <cstdint>
#include <iostream>

void put_u32(std::array<std::uint8_t, 44>& h, int pos, std::uint32_t v) {
    // TODO: write 4 bytes, least significant first
}

int main() {
    std::array<std::uint8_t, 44> header{};
    put_u32(header, 24, 48000);  // sample rate lives at offset 24
    std::cout << "TODO\n";
}
''', solution=r'''
#include <array>
#include <cstdint>
#include <iostream>

using Header = std::array<std::uint8_t, 44>;

void put_u16(Header& h, std::size_t pos, std::uint16_t v) {
    h[pos] = static_cast<std::uint8_t>(v & 0xFF);
    h[pos + 1] = static_cast<std::uint8_t>(v >> 8);
}
void put_u32(Header& h, std::size_t pos, std::uint32_t v) {
    for (std::size_t i = 0; i < 4; ++i) h[pos + i] = static_cast<std::uint8_t>(v >> (8 * i));
}
std::uint16_t get_u16(const Header& h, std::size_t pos) {
    return static_cast<std::uint16_t>(h[pos] | (h[pos + 1] << 8));
}
std::uint32_t get_u32(const Header& h, std::size_t pos) {
    std::uint32_t v = 0;
    for (std::size_t i = 0; i < 4; ++i) v |= std::uint32_t{h[pos + i]} << (8 * i);
    return v;
}

int main() {
    constexpr std::uint32_t sample_rate = 48'000;
    constexpr std::uint16_t channels = 2, bits = 16;
    constexpr std::uint32_t byte_rate = sample_rate * channels * bits / 8;
    constexpr std::uint32_t data_size = byte_rate * 1;  // one second of audio

    Header h{};
    const char* tags[] = {"RIFF", "WAVE", "fmt ", "data"};
    const std::size_t tag_pos[] = {0, 8, 12, 36};
    for (int t = 0; t < 4; ++t)
        for (std::size_t i = 0; i < 4; ++i) h[tag_pos[t] + i] = static_cast<std::uint8_t>(tags[t][i]);
    put_u32(h, 4, 36 + data_size);
    put_u32(h, 16, 16);      // fmt chunk size
    put_u16(h, 20, 1);       // PCM
    put_u16(h, 22, channels);
    put_u32(h, 24, sample_rate);
    put_u32(h, 28, byte_rate);
    put_u16(h, 32, static_cast<std::uint16_t>(channels * bits / 8));  // block align
    put_u16(h, 34, bits);
    put_u32(h, 40, data_size);

    std::cout << "format=" << get_u16(h, 20) << " channels=" << get_u16(h, 22)
              << " rate=" << get_u32(h, 24) << " byte_rate=" << get_u32(h, 28)
              << " bits=" << get_u16(h, 34) << " data=" << get_u32(h, 40) << '\n';
}
'''))
