# Feature checklist

This page lists the important C++ language features and standard library topics, each mapped to the lesson
that teaches it and tagged with the standard that introduced it (or made it usable in its modern form).
It is **generated from the lesson sources**, so if a row is here, the lesson really covers it.

Tags: **C++98/03** (classic), **C++11**, **C++14**, **C++17**, **C++20**, **C++23**, **C++26 (preview)**.
A "—" tag means a tool or practice rather than a language feature.

Use it as a checklist: tick off what you can explain to a colleague without notes.

## Basics: toolchain & compilation

| Feature | Standard | Taught in |
|---|---|---|
| g++ / clang++ command line, warnings flags | — | [Lesson 1.1](../week01/lesson01.md) |
| CMake basics (project, add_executable, target_compile_features) | — | [Lesson 1.1](../week01/lesson01.md) |
| Compiler Explorer (godbolt.org) | — | [Lesson 1.1](../week01/lesson01.md) |
| `main`, return codes, `std::cout` | C++98 | [Lesson 1.1](../week01/lesson01.md) |
| Preprocessor: #include, #define, #if, include guards, #pragma once | C++98 | [Lesson 1.2](../week01/lesson02.md) |
| Translation units, declarations vs definitions | C++98 | [Lesson 1.2](../week01/lesson02.md) |
| Linking, undefined reference errors | — | [Lesson 1.2](../week01/lesson02.md) |
| One Definition Rule (ODR), `inline` variables | C++17 | [Lesson 1.2](../week01/lesson02.md) |
| Headers vs source files, `static`/anonymous namespaces (internal linkage) | C++98 | [Lesson 1.2](../week01/lesson02.md) |

## Basics: types & values

| Feature | Standard | Taught in |
|---|---|---|
| Fundamental types: bool, char, int, long, long long, float, double | C++98 | [Lesson 1.3](../week01/lesson03.md) |
| Integer literals: hex, octal, binary `0b`, digit separators `'` | C++14 | [Lesson 1.3](../week01/lesson03.md) |
| `<cstdint>`: int32_t, uint8_t, size_t... | C++11 | [Lesson 1.3](../week01/lesson03.md) |
| `<limits>`: std::numeric_limits | C++98 | [Lesson 1.3](../week01/lesson03.md) |
| `char8_t`, `char16_t`, `char32_t` | C++20 | [Lesson 1.3](../week01/lesson03.md) |
| `sizeof`, `alignof` | C++11 | [Lesson 1.3](../week01/lesson03.md) |
| `nullptr` | C++11 | [Lesson 1.3](../week01/lesson03.md) |
| Floating point basics and precision | C++98 | [Lesson 1.3](../week01/lesson03.md) |
| Variable initialization forms: `=`, `()`, `{}` | C++11 | [Lesson 1.4](../week01/lesson04.md) |
| Brace initialization prevents narrowing | C++11 | [Lesson 1.4](../week01/lesson04.md) |
| `auto` type deduction | C++11 | [Lesson 1.4](../week01/lesson04.md) |
| `const` | C++98 | [Lesson 1.4](../week01/lesson04.md) |
| `constexpr` variables | C++11 | [Lesson 1.4](../week01/lesson04.md) |
| `decltype` | C++11 | [Lesson 1.4](../week01/lesson04.md) |
| Uninitialized variables (indeterminate values) | C++98 | [Lesson 1.4](../week01/lesson04.md) |
| Arithmetic, comparison, logical operators; precedence | C++98 | [Lesson 1.5](../week01/lesson05.md) |
| Integer promotion and usual arithmetic conversions | C++98 | [Lesson 1.5](../week01/lesson05.md) |
| Signed/unsigned comparison pitfalls; `std::cmp_less` etc. | C++20 | [Lesson 1.5](../week01/lesson05.md) |
| Signed overflow is UB; unsigned wraps | C++98 | [Lesson 1.5](../week01/lesson05.md) |
| `static_cast` and other named casts | C++98 | [Lesson 1.5](../week01/lesson05.md) |
| Order of evaluation rules (C++17 changes) | C++17 | [Lesson 1.5](../week01/lesson05.md) |
| Unscoped `enum` vs scoped `enum class`, underlying type | C++11 | [Lesson 2.5](../week02/lesson05.md) |
| `using enum` | C++20 | [Lesson 2.5](../week02/lesson05.md) |
| `std::to_underlying` | C++23 | [Lesson 2.5](../week02/lesson05.md) |
| `struct` basics, default member initializers | C++11 | [Lesson 2.5](../week02/lesson05.md) |
| Attributes: `[[nodiscard]]`, `[[maybe_unused]]`, `[[deprecated]]`, `[[noreturn]]` | C++17 | [Lesson 2.5](../week02/lesson05.md) |
| `[[likely]]` / `[[unlikely]]`, `[[no_unique_address]]` | C++20 | [Lesson 2.5](../week02/lesson05.md) |
| `[[assume]]` | C++23 | [Lesson 2.5](../week02/lesson05.md) |

## Basics: control flow & functions

| Feature | Standard | Taught in |
|---|---|---|
| if / else, switch, fallthrough and `[[fallthrough]]` | C++17 | [Lesson 2.1](../week02/lesson01.md) |
| `if` and `switch` with initializer | C++17 | [Lesson 2.1](../week02/lesson01.md) |
| while, do-while, for, break, continue | C++98 | [Lesson 2.1](../week02/lesson01.md) |
| Range-based for, with initializer | C++20 | [Lesson 2.1](../week02/lesson01.md) |
| Conditional operator `?:` | C++98 | [Lesson 2.1](../week02/lesson01.md) |
| Function declarations, definitions, return types, trailing return type | C++11 | [Lesson 2.2](../week02/lesson02.md) |
| Function overloading and overload resolution basics | C++98 | [Lesson 2.2](../week02/lesson02.md) |
| Default arguments | C++98 | [Lesson 2.2](../week02/lesson02.md) |
| `auto` return type deduction | C++14 | [Lesson 2.2](../week02/lesson02.md) |
| Abbreviated function templates (`auto` parameters) | C++20 | [Lesson 2.2](../week02/lesson02.md) |
| `inline` functions | C++98 | [Lesson 2.2](../week02/lesson02.md) |
| Recursion | C++98 | [Lesson 2.2](../week02/lesson02.md) |
| Lvalue references `T&` | C++98 | [Lesson 2.3](../week02/lesson03.md) |
| const references bind to temporaries (lifetime extension) | C++98 | [Lesson 2.3](../week02/lesson03.md) |
| Parameter passing guidelines: by value, `const T&`, `T&` | — | [Lesson 2.3](../week02/lesson03.md) |
| `auto` deduction drops references and top-level const; `auto&`, `const auto&` | C++11 | [Lesson 2.3](../week02/lesson03.md) |
| Dangling references | C++98 | [Lesson 2.3](../week02/lesson03.md) |
| Block scope and name hiding | C++98 | [Lesson 2.4](../week02/lesson04.md) |
| Object lifetime; destruction in reverse order | C++98 | [Lesson 2.4](../week02/lesson04.md) |
| Storage duration: automatic, static, thread, dynamic | C++11 | [Lesson 2.4](../week02/lesson04.md) |
| Function-local `static` (thread-safe init) | C++11 | [Lesson 2.4](../week02/lesson04.md) |
| Namespaces, nested namespaces `a::b::c`, inline namespaces | C++17 | [Lesson 2.4](../week02/lesson04.md) |
| `using` declarations vs `using namespace` | C++98 | [Lesson 2.4](../week02/lesson04.md) |
| Static initialization order fiasco | — | [Lesson 2.4](../week02/lesson04.md) |

## Basics: memory

| Feature | Standard | Taught in |
|---|---|---|
| Built-in (C) arrays and array-to-pointer decay | C++98 | [Lesson 3.1](../week03/lesson01.md) |
| `std::array` | C++11 | [Lesson 3.1](../week03/lesson01.md) |
| `std::size`, `std::ssize`, `std::data` | C++20 | [Lesson 3.1](../week03/lesson01.md) |
| `std::span` (non-owning view) | C++20 | [Lesson 3.1](../week03/lesson01.md) |
| Out-of-bounds access is UB; `.at()` bounds-checked | C++98 | [Lesson 3.1](../week03/lesson01.md) |
| Pointers, `&` address-of, `*` dereference, `->` | C++98 | [Lesson 3.2](../week03/lesson02.md) |
| `nullptr` checks | C++11 | [Lesson 3.2](../week03/lesson02.md) |
| Pointer arithmetic within an array | C++98 | [Lesson 3.2](../week03/lesson02.md) |
| `const T*` vs `T* const` | C++98 | [Lesson 3.2](../week03/lesson02.md) |
| Pointers vs references: when to use which | — | [Lesson 3.2](../week03/lesson02.md) |
| `void*` and why to avoid it | C++98 | [Lesson 3.2](../week03/lesson02.md) |
| Stack vs heap, `new`/`delete`, `new[]`/`delete[]` | C++98 | [Lesson 3.3](../week03/lesson03.md) |
| Memory leaks, double free, use-after-free | — | [Lesson 3.3](../week03/lesson03.md) |
| Undefined behaviour: what it means for the optimizer | — | [Lesson 3.3](../week03/lesson03.md) |
| AddressSanitizer / UBSan first look | — | [Lesson 3.3](../week03/lesson03.md) |
| Placement new (preview) | C++98 | [Lesson 3.3](../week03/lesson03.md) |
| C strings (`const char*`, NUL terminator), `<cstring>` pitfalls | C++98 | [Lesson 3.4](../week03/lesson04.md) |
| `std::string` basics, SSO | C++98 | [Lesson 3.4](../week03/lesson04.md) |
| `std::string_view` | C++17 | [Lesson 3.4](../week03/lesson04.md) |
| `starts_with` / `ends_with` | C++20 | [Lesson 3.4](../week03/lesson04.md) |
| `contains` | C++23 | [Lesson 3.4](../week03/lesson04.md) |
| `std::string` literals `"x"s` and `"x"sv` | C++14 | [Lesson 3.4](../week03/lesson04.md) |
| Dangling string_view pitfalls | C++17 | [Lesson 3.4](../week03/lesson04.md) |
| Bitwise operators `& | ^ ~ << >>`, masks | C++98 | [Lesson 3.5](../week03/lesson05.md) |
| Shift pitfalls (shifting by >= width is UB; negative values) | C++20 | [Lesson 3.5](../week03/lesson05.md) |
| `std::byte` | C++17 | [Lesson 3.5](../week03/lesson05.md) |
| `<bit>`: popcount, countl_zero, rotl, bit_ceil, has_single_bit | C++20 | [Lesson 3.5](../week03/lesson05.md) |
| `std::bit_cast` | C++20 | [Lesson 3.5](../week03/lesson05.md) |
| `std::endian`, `std::byteswap` | C++23 | [Lesson 3.5](../week03/lesson05.md) |
| Two's complement guaranteed | C++20 | [Lesson 3.5](../week03/lesson05.md) |

## OOP: classes

| Feature | Standard | Taught in |
|---|---|---|
| `class` vs `struct`, `public`/`private`/`protected` | C++98 | [Lesson 4.1](../week04/lesson01.md) |
| Member functions, `this` | C++98 | [Lesson 4.1](../week04/lesson01.md) |
| `const` member functions, `mutable` | C++98 | [Lesson 4.1](../week04/lesson01.md) |
| Class invariants | — | [Lesson 4.1](../week04/lesson01.md) |
| Ref-qualified member functions (`&`, `&&`) | C++11 | [Lesson 4.1](../week04/lesson01.md) |
| Constructors, member initializer lists | C++98 | [Lesson 4.2](../week04/lesson02.md) |
| Default member initializers | C++11 | [Lesson 4.2](../week04/lesson02.md) |
| Delegating constructors | C++11 | [Lesson 4.2](../week04/lesson02.md) |
| `= default`, `= delete` | C++11 | [Lesson 4.2](../week04/lesson02.md) |
| Member initialization order = declaration order | C++98 | [Lesson 4.2](../week04/lesson02.md) |
| List-initialization and the `std::initializer_list` constructor pitfall | C++11 | [Lesson 4.2](../week04/lesson02.md) |
| Value-, default-, zero-initialization; most vexing parse | C++11 | [Lesson 4.2](../week04/lesson02.md) |
| Destructors | C++98 | [Lesson 4.2](../week04/lesson02.md) |
| RAII (Resource Acquisition Is Initialization) | C++98 | [Lesson 4.3](../week04/lesson03.md) |
| Destructors run during stack unwinding | C++98 | [Lesson 4.3](../week04/lesson03.md) |
| Scope guards | — | [Lesson 4.3](../week04/lesson03.md) |
| Wrapping C handles (FILE*, fds) in RAII types | — | [Lesson 4.3](../week04/lesson03.md) |
| Non-copyable resource types | C++11 | [Lesson 4.3](../week04/lesson03.md) |
| `explicit` constructors and `explicit(bool)` | C++20 | [Lesson 4.4](../week04/lesson04.md) |
| Conversion operators, `explicit operator bool` | C++11 | [Lesson 4.4](../week04/lesson04.md) |
| `static` data members and functions, `inline static` | C++17 | [Lesson 4.4](../week04/lesson04.md) |
| `friend` functions and classes | C++98 | [Lesson 4.4](../week04/lesson04.md) |
| Nested classes and local classes | C++98 | [Lesson 4.4](../week04/lesson04.md) |
| Operator overloading: member vs non-member, canonical forms | C++98 | [Lesson 4.5](../week04/lesson05.md) |
| Three-way comparison `operator<=>` | C++20 | [Lesson 4.5](../week04/lesson05.md) |
| Defaulted comparisons `= default` | C++20 | [Lesson 4.5](../week04/lesson05.md) |
| `std::strong_ordering`, `weak_ordering`, `partial_ordering` | C++20 | [Lesson 4.5](../week04/lesson05.md) |
| Rewritten comparison candidates (`a != b` from `==`) | C++20 | [Lesson 4.5](../week04/lesson05.md) |
| Overloading `[]` (multi-dimensional subscript in C++23), `()` | C++23 | [Lesson 4.5](../week04/lesson05.md) |

## OOP: value semantics

| Feature | Standard | Taught in |
|---|---|---|
| Copy constructor, copy assignment operator | C++98 | [Lesson 5.1](../week05/lesson01.md) |
| Shallow vs deep copy | — | [Lesson 5.1](../week05/lesson01.md) |
| Rule of Three | C++98 | [Lesson 5.1](../week05/lesson01.md) |
| Copy-and-swap idiom, self-assignment | C++98 | [Lesson 5.1](../week05/lesson01.md) |
| Implicitly generated special member functions | C++11 | [Lesson 5.1](../week05/lesson01.md) |
| Value categories: lvalue, prvalue, xvalue (glvalue, rvalue) | C++11 | [Lesson 5.2](../week05/lesson02.md) |
| Rvalue references `T&&` | C++11 | [Lesson 5.2](../week05/lesson02.md) |
| Overloading on `&` vs `&&` parameters | C++11 | [Lesson 5.2](../week05/lesson02.md) |
| Temporaries and temporary materialization | C++17 | [Lesson 5.2](../week05/lesson02.md) |
| `decltype((x))` reveals value category | C++11 | [Lesson 5.2](../week05/lesson02.md) |
| Move constructor, move assignment | C++11 | [Lesson 5.3](../week05/lesson03.md) |
| `std::move` (it's just a cast) | C++11 | [Lesson 5.3](../week05/lesson03.md) |
| Moved-from state: valid but unspecified | C++11 | [Lesson 5.3](../week05/lesson03.md) |
| `noexcept` moves and `std::vector` reallocation | C++11 | [Lesson 5.3](../week05/lesson03.md) |
| Rule of Five, Rule of Zero | C++11 | [Lesson 5.3](../week05/lesson03.md) |
| Move-only types | C++11 | [Lesson 5.3](../week05/lesson03.md) |
| Guaranteed copy elision for prvalues | C++17 | [Lesson 5.4](../week05/lesson04.md) |
| Named return value optimization (NRVO) | C++98 | [Lesson 5.4](../week05/lesson04.md) |
| Implicit move on return | C++20 | [Lesson 5.4](../week05/lesson04.md) |
| Sink parameters: pass by value and move | C++11 | [Lesson 5.4](../week05/lesson04.md) |
| Aggregates and aggregate initialization | C++98 | [Lesson 5.5](../week05/lesson05.md) |
| Designated initializers | C++20 | [Lesson 5.5](../week05/lesson05.md) |
| Aggregate init with parentheses | C++20 | [Lesson 5.5](../week05/lesson05.md) |
| Structured bindings | C++17 | [Lesson 5.5](../week05/lesson05.md) |
| Structured bindings for your own types (tuple protocol) | C++17 | [Lesson 5.5](../week05/lesson05.md) |
| User-defined literals | C++11 | [Lesson 5.5](../week05/lesson05.md) |
| Standard literals: `s`, `sv`, `ms`, `i` | C++14 | [Lesson 5.5](../week05/lesson05.md) |

## C++26 preview items

C++26 was finalized in 2025–2026; compilers are still implementing it. These are covered in
[Lesson 16.5: C++26 preview](../week16/lesson05.md):

| Feature | Status |
|---|---|
| Static reflection (`^^T`, `std::meta`, splicers `[: :]`) | C++26 (P2996) — preview, experimental compilers only |
| Contracts (`pre`, `post`, `contract_assert`) | C++26 (P2900) — preview |
| `std::execution` (senders/receivers) | C++26 (P2300) — preview; usable today via NVIDIA stdexec |
| `std::inplace_vector` | C++26 (P0843) — preview |
| `#embed`, pack indexing, `= delete("reason")`, placeholder `_` variables | C++26 — preview |
| Hardened standard library, erroneous behaviour for uninitialized reads | C++26 — preview |
