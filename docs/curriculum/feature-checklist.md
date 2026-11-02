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

## OOP: inheritance & polymorphism

| Feature | Standard | Taught in |
|---|---|---|
| Public/protected/private inheritance | C++98 | [Lesson 6.1](../week06/lesson01.md) |
| Construction/destruction order of bases and members | C++98 | [Lesson 6.1](../week06/lesson01.md) |
| Calling base constructors; inheriting constructors `using Base::Base` | C++11 | [Lesson 6.1](../week06/lesson01.md) |
| Name hiding in derived classes, `using Base::f` | C++98 | [Lesson 6.1](../week06/lesson01.md) |
| `protected` members | C++98 | [Lesson 6.1](../week06/lesson01.md) |
| Virtual functions and dynamic dispatch | C++98 | [Lesson 6.2](../week06/lesson02.md) |
| `override` and `final` | C++11 | [Lesson 6.2](../week06/lesson02.md) |
| Vtables and vptr (implementation model) | — | [Lesson 6.2](../week06/lesson02.md) |
| Virtual calls in constructors/destructors | C++98 | [Lesson 6.2](../week06/lesson02.md) |
| Covariant return types | C++98 | [Lesson 6.2](../week06/lesson02.md) |
| Devirtualization | — | [Lesson 6.2](../week06/lesson02.md) |
| Pure virtual functions, abstract classes | C++98 | [Lesson 6.3](../week06/lesson03.md) |
| Interfaces as abstract base classes | — | [Lesson 6.3](../week06/lesson03.md) |
| Virtual destructors (and when not to) | C++98 | [Lesson 6.3](../week06/lesson03.md) |
| Object slicing | C++98 | [Lesson 6.3](../week06/lesson03.md) |
| Polymorphic copy: `clone()` | — | [Lesson 6.3](../week06/lesson03.md) |
| Non-virtual interface (NVI) idiom | — | [Lesson 6.3](../week06/lesson03.md) |
| Multiple inheritance | C++98 | [Lesson 6.4](../week06/lesson04.md) |
| The diamond problem, virtual inheritance | C++98 | [Lesson 6.4](../week06/lesson04.md) |
| Pointer adjustment with multiple bases | — | [Lesson 6.4](../week06/lesson04.md) |
| Mixins / interface-only multiple inheritance | — | [Lesson 6.4](../week06/lesson04.md) |
| `dynamic_cast` (pointers and references) | C++98 | [Lesson 6.5](../week06/lesson05.md) |
| `typeid`, `std::type_info`, `<typeinfo>` | C++98 | [Lesson 6.5](../week06/lesson05.md) |
| `std::type_index` | C++11 | [Lesson 6.5](../week06/lesson05.md) |
| `std::any` | C++17 | [Lesson 6.5](../week06/lesson05.md) |
| `-fno-rtti` and its consequences | — | [Lesson 6.5](../week06/lesson05.md) |

## Templates & generic programming

| Feature | Standard | Taught in |
|---|---|---|
| Function templates | C++98 | [Lesson 7.1](../week07/lesson01.md) |
| Template argument deduction | C++98 | [Lesson 7.1](../week07/lesson01.md) |
| Explicit template arguments | C++98 | [Lesson 7.1](../week07/lesson01.md) |
| Abbreviated function templates (`auto` parameters) | C++20 | [Lesson 7.1](../week07/lesson01.md) |
| Two-phase lookup, `typename` disambiguator | C++98 | [Lesson 7.1](../week07/lesson01.md) |
| Templates in headers (instantiation model) | C++98 | [Lesson 7.1](../week07/lesson01.md) |
| Class templates | C++98 | [Lesson 7.2](../week07/lesson02.md) |
| Member function templates | C++98 | [Lesson 7.2](../week07/lesson02.md) |
| Full specialization | C++98 | [Lesson 7.2](../week07/lesson02.md) |
| Partial specialization | C++98 | [Lesson 7.2](../week07/lesson02.md) |
| Class template argument deduction (CTAD) and deduction guides | C++17 | [Lesson 7.2](../week07/lesson02.md) |
| Alias templates (`using`) | C++11 | [Lesson 7.2](../week07/lesson02.md) |
| Variable templates | C++14 | [Lesson 7.2](../week07/lesson02.md) |
| Non-type template parameters (NTTP) | C++98 | [Lesson 7.3](../week07/lesson03.md) |
| `auto` NTTP | C++17 | [Lesson 7.3](../week07/lesson03.md) |
| Class-type NTTPs (structural types) | C++20 | [Lesson 7.3](../week07/lesson03.md) |
| Variadic templates, parameter packs, `sizeof...` | C++11 | [Lesson 7.3](../week07/lesson03.md) |
| Fold expressions | C++17 | [Lesson 7.3](../week07/lesson03.md) |
| Template template parameters | C++98 | [Lesson 7.3](../week07/lesson03.md) |
| Forwarding (universal) references `T&&` | C++11 | [Lesson 7.4](../week07/lesson04.md) |
| Reference collapsing | C++11 | [Lesson 7.4](../week07/lesson04.md) |
| `std::forward` | C++11 | [Lesson 7.4](../week07/lesson04.md) |
| `decltype(auto)` return types | C++14 | [Lesson 7.4](../week07/lesson04.md) |
| Perfect forwarding of packs (`emplace`, `make_unique`) | C++11 | [Lesson 7.4](../week07/lesson04.md) |
| `<type_traits>` queries and transformations | C++11 | [Lesson 7.5](../week07/lesson05.md) |
| `_v` and `_t` helpers | C++14/17 | [Lesson 7.5](../week07/lesson05.md) |
| `if constexpr` | C++17 | [Lesson 7.5](../week07/lesson05.md) |
| SFINAE and `std::enable_if` | C++11 | [Lesson 7.5](../week07/lesson05.md) |
| `std::void_t` detection idiom | C++17 | [Lesson 7.5](../week07/lesson05.md) |
| `std::declval` | C++11 | [Lesson 7.5](../week07/lesson05.md) |
| `std::conditional`, `std::decay`, `std::remove_cvref` | C++11/20 | [Lesson 7.5](../week07/lesson05.md) |
| Concepts (`concept`) | C++20 | [Lesson 8.1](../week08/lesson01.md) |
| `requires` clauses and `requires` expressions | C++20 | [Lesson 8.1](../week08/lesson01.md) |
| Standard concepts (`<concepts>`, iterator/range concepts) | C++20 | [Lesson 8.1](../week08/lesson01.md) |
| Constrained `auto` (`std::integral auto x`) | C++20 | [Lesson 8.1](../week08/lesson01.md) |
| Subsumption / overload ordering by constraints | C++20 | [Lesson 8.1](../week08/lesson01.md) |
| CRTP (curiously recurring template pattern) | C++98 | [Lesson 8.5](../week08/lesson05.md) |
| Explicit object parameter (deducing `this`) | C++23 | [Lesson 8.5](../week08/lesson05.md) |
| Static polymorphism vs dynamic polymorphism | — | [Lesson 8.5](../week08/lesson05.md) |
| Template metaprogramming basics (recursive templates, type lists) | C++11 | [Lesson 8.5](../week08/lesson05.md) |
| `std::integer_sequence` / `std::index_sequence` | C++14 | [Lesson 8.5](../week08/lesson05.md) |
| Expression templates (overview) | — | [Lesson 8.5](../week08/lesson05.md) |

## Compile-time programming

| Feature | Standard | Taught in |
|---|---|---|
| `constexpr` variables and functions | C++11 (relaxed C++14) | [Lesson 8.2](../week08/lesson02.md) |
| `constexpr` virtual, try, dynamic allocation in constant evaluation | C++20 | [Lesson 8.2](../week08/lesson02.md) |
| `consteval` (immediate functions) | C++20 | [Lesson 8.2](../week08/lesson02.md) |
| `constinit` | C++20 | [Lesson 8.2](../week08/lesson02.md) |
| `if consteval` | C++23 | [Lesson 8.2](../week08/lesson02.md) |
| `std::is_constant_evaluated` | C++20 | [Lesson 8.2](../week08/lesson02.md) |
| Static initialization order fiasco | C++98 | [Lesson 8.2](../week08/lesson02.md) |

## Functional programming

| Feature | Standard | Taught in |
|---|---|---|
| Lambda expressions, captures by value/reference | C++11 | [Lesson 8.3](../week08/lesson03.md) |
| Init captures, `mutable` | C++14 | [Lesson 8.3](../week08/lesson03.md) |
| Generic lambdas | C++14 | [Lesson 8.3](../week08/lesson03.md) |
| `constexpr` lambdas | C++17 | [Lesson 8.3](../week08/lesson03.md) |
| `[*this]` capture | C++17 | [Lesson 8.3](../week08/lesson03.md) |
| Template lambdas `[]<typename T>` | C++20 | [Lesson 8.3](../week08/lesson03.md) |
| Lambdas in unevaluated contexts, default-constructible stateless lambdas | C++20 | [Lesson 8.3](../week08/lesson03.md) |
| `static operator()` lambdas | C++23 | [Lesson 8.3](../week08/lesson03.md) |
| Immediately-invoked lambdas (IILE) | — | [Lesson 8.3](../week08/lesson03.md) |
| `std::function` | C++11 | [Lesson 8.4](../week08/lesson04.md) |
| `std::move_only_function` | C++23 | [Lesson 8.4](../week08/lesson04.md) |
| `std::function_ref` | C++26 (preview) | [Lesson 8.4](../week08/lesson04.md) |
| `std::invoke`, `std::invoke_r` | C++17/23 | [Lesson 8.4](../week08/lesson04.md) |
| `std::bind_front`, `std::bind_back` | C++20/23 | [Lesson 8.4](../week08/lesson04.md) |
| Member function pointers | C++98 | [Lesson 8.4](../week08/lesson04.md) |
| Type erasure (concept/model pattern) | — | [Lesson 8.4](../week08/lesson04.md) |

## Error handling

| Feature | Standard | Taught in |
|---|---|---|
| `throw`, `try`, `catch`, rethrow `throw;` | C++98 | [Lesson 9.1](../week09/lesson01.md) |
| Standard exception hierarchy (`<stdexcept>`) | C++98 | [Lesson 9.1](../week09/lesson01.md) |
| Stack unwinding and RAII | C++98 | [Lesson 9.1](../week09/lesson01.md) |
| `std::exception_ptr`, `std::current_exception`, `std::rethrow_exception` | C++11 | [Lesson 9.1](../week09/lesson01.md) |
| `std::nested_exception`, `std::throw_with_nested` | C++11 | [Lesson 9.1](../week09/lesson01.md) |
| Function-try-blocks | C++98 | [Lesson 9.1](../week09/lesson01.md) |
| `-fno-exceptions` builds | — | [Lesson 9.1](../week09/lesson01.md) |
| Exception safety guarantees (nothrow, strong, basic) | — | [Lesson 9.2](../week09/lesson02.md) |
| `noexcept` specifier and operator | C++11 | [Lesson 9.2](../week09/lesson02.md) |
| Conditional `noexcept(expr)` | C++11 | [Lesson 9.2](../week09/lesson02.md) |
| Destructors are implicitly `noexcept` | C++11 | [Lesson 9.2](../week09/lesson02.md) |
| Copy-and-swap for the strong guarantee | — | [Lesson 9.2](../week09/lesson02.md) |
| `std::move_if_noexcept` | C++11 | [Lesson 9.2](../week09/lesson02.md) |
| `std::optional` | C++17 | [Lesson 9.3](../week09/lesson03.md) |
| Monadic `optional`: `and_then`, `transform`, `or_else` | C++23 | [Lesson 9.3](../week09/lesson03.md) |
| `std::variant`, `std::visit`, `std::holds_alternative`, `std::get_if` | C++17 | [Lesson 9.3](../week09/lesson03.md) |
| Overload pattern for visitors | C++17 | [Lesson 9.3](../week09/lesson03.md) |
| `std::monostate` | C++17 | [Lesson 9.3](../week09/lesson03.md) |
| `valueless_by_exception` | C++17 | [Lesson 9.3](../week09/lesson03.md) |
| `std::expected<T, E>`, `std::unexpected` | C++23 | [Lesson 9.4](../week09/lesson04.md) |
| Monadic `expected`: `and_then`, `transform`, `or_else`, `transform_error` | C++23 | [Lesson 9.4](../week09/lesson04.md) |
| `std::error_code`, `std::error_condition`, `std::system_error` | C++11 | [Lesson 9.4](../week09/lesson04.md) |
| `std::errc` | C++11 | [Lesson 9.4](../week09/lesson04.md) |
| `[[nodiscard]]` on result types | C++17 | [Lesson 9.4](../week09/lesson04.md) |
| Choosing exceptions vs. expected vs. optional vs. terminate | — | [Lesson 9.4](../week09/lesson04.md) |
| `assert` and `NDEBUG` | C++98 | [Lesson 9.5](../week09/lesson05.md) |
| `static_assert` (with and without message) | C++11/17 | [Lesson 9.5](../week09/lesson05.md) |
| Contracts: `pre`, `post`, `contract_assert` | C++26 (preview) | [Lesson 9.5](../week09/lesson05.md) |
| Undefined behaviour catalogue | — | [Lesson 9.5](../week09/lesson05.md) |
| Unspecified vs implementation-defined vs undefined | — | [Lesson 9.5](../week09/lesson05.md) |
| Erroneous behaviour for uninitialized reads | C++26 (preview) | [Lesson 9.5](../week09/lesson05.md) |
| `std::unreachable` | C++23 | [Lesson 9.5](../week09/lesson05.md) |

## Standard library: containers

| Feature | Standard | Taught in |
|---|---|---|
| `std::vector`: size vs capacity, growth, `reserve`, `shrink_to_fit` | C++98 | [Lesson 10.1](../week10/lesson01.md) |
| `emplace_back` vs `push_back` | C++11 | [Lesson 10.1](../week10/lesson01.md) |
| Iterator invalidation rules | C++98 | [Lesson 10.1](../week10/lesson01.md) |
| `std::erase` / `std::erase_if` (uniform erasure) | C++20 | [Lesson 10.1](../week10/lesson01.md) |
| Erase-remove idiom | C++98 | [Lesson 10.1](../week10/lesson01.md) |
| `std::vector<bool>` specialization | C++98 | [Lesson 10.1](../week10/lesson01.md) |
| `append_range`, `insert_range` | C++23 | [Lesson 10.1](../week10/lesson01.md) |
| `std::array`, `std::to_array` | C++11/20 | [Lesson 10.2](../week10/lesson02.md) |
| `std::deque` | C++98 | [Lesson 10.2](../week10/lesson02.md) |
| `std::list`, `splice` | C++98 | [Lesson 10.2](../week10/lesson02.md) |
| `std::forward_list` | C++11 | [Lesson 10.2](../week10/lesson02.md) |
| Complexity guarantees and cache effects | — | [Lesson 10.2](../week10/lesson02.md) |
| `std::map`, `std::set`, `multimap`, `multiset` | C++98 | [Lesson 10.3](../week10/lesson03.md) |
| `std::unordered_map`, `unordered_set` (+multi) | C++11 | [Lesson 10.3](../week10/lesson03.md) |
| `try_emplace`, `insert_or_assign` | C++17 | [Lesson 10.3](../week10/lesson03.md) |
| Node handles: `extract`, `merge` | C++17 | [Lesson 10.3](../week10/lesson03.md) |
| `contains` | C++20 | [Lesson 10.3](../week10/lesson03.md) |
| Heterogeneous lookup (transparent comparators/hashes) | C++14/20 | [Lesson 10.3](../week10/lesson03.md) |
| Custom hash functions, `std::hash` specialization | C++11 | [Lesson 10.3](../week10/lesson03.md) |
| `std::stack`, `std::queue` | C++98 | [Lesson 10.4](../week10/lesson04.md) |
| `std::priority_queue` | C++98 | [Lesson 10.4](../week10/lesson04.md) |
| `std::flat_map`, `std::flat_set` (+multi) | C++23 | [Lesson 10.4](../week10/lesson04.md) |
| Sorted vector as a set/map | — | [Lesson 10.4](../week10/lesson04.md) |
| `std::span` (static and dynamic extent) | C++20 | [Lesson 10.5](../week10/lesson05.md) |
| `std::mdspan`, extents, layouts | C++23 | [Lesson 10.5](../week10/lesson05.md) |
| Multidimensional `operator[]` | C++23 | [Lesson 10.5](../week10/lesson05.md) |
| `std::inplace_vector` | C++26 (preview) | [Lesson 10.5](../week10/lesson05.md) |
| Non-owning views and lifetime | — | [Lesson 10.5](../week10/lesson05.md) |

## Standard library: iterators

| Feature | Standard | Taught in |
|---|---|---|
| Iterator categories (input, output, forward, bidirectional, random access, contiguous) | C++98/20 | [Lesson 10.6](../week10/lesson06.md) |
| C++20 iterator concepts | C++20 | [Lesson 10.6](../week10/lesson06.md) |
| `std::begin/end/size/data/ssize` | C++11/17/20 | [Lesson 10.6](../week10/lesson06.md) |
| Iterator adaptors: `reverse_iterator`, `back_inserter`, `move_iterator`, `istream_iterator` | C++98/11 | [Lesson 10.6](../week10/lesson06.md) |
| `std::advance`, `next`, `prev`, `distance` | C++98/11 | [Lesson 10.6](../week10/lesson06.md) |
| Writing a custom iterator | C++20 | [Lesson 10.6](../week10/lesson06.md) |
| Sentinels | C++20 | [Lesson 10.6](../week10/lesson06.md) |

## Standard library: algorithms

| Feature | Standard | Taught in |
|---|---|---|
| Non-modifying algorithms: `find`, `find_if`, `count_if`, `all_of/any_of/none_of`, `mismatch`, `search` | C++98/11 | [Lesson 11.1](../week11/lesson01.md) |
| Sorting: `sort`, `stable_sort`, `partial_sort`, `nth_element` | C++98 | [Lesson 11.1](../week11/lesson01.md) |
| Binary search: `lower_bound`, `upper_bound`, `equal_range`, `binary_search` | C++98 | [Lesson 11.1](../week11/lesson01.md) |
| `min/max/minmax/clamp`, `min_element/max_element` | C++98/11/17 | [Lesson 11.1](../week11/lesson01.md) |
| Strict weak ordering requirement | C++98 | [Lesson 11.1](../week11/lesson01.md) |
| Range algorithms `std::ranges::*` with projections | C++20 | [Lesson 11.1](../week11/lesson01.md) |
| Modifying algorithms: `copy_if`, `transform`, `replace_if`, `fill`, `generate`, `rotate`, `reverse`, `unique`, `shuffle` | C++98/11 | [Lesson 11.2](../week11/lesson02.md) |
| Set algorithms on sorted ranges: `set_union`, `set_intersection`, `includes`, `merge` | C++98 | [Lesson 11.2](../week11/lesson02.md) |
| Heap algorithms: `make_heap`, `push_heap`, `pop_heap` | C++98 | [Lesson 11.2](../week11/lesson02.md) |
| `<numeric>`: `accumulate`, `reduce`, `transform_reduce`, `inner_product`, `partial_sum`, `inclusive_scan`, `iota`, `gcd`, `lcm`, `midpoint` | C++98/17/20 | [Lesson 11.2](../week11/lesson02.md) |
| `std::ranges::fold_left` | C++23 | [Lesson 11.2](../week11/lesson02.md) |
| Output ranges and `back_inserter` | C++98 | [Lesson 11.2](../week11/lesson02.md) |

## Standard library: ranges

| Feature | Standard | Taught in |
|---|---|---|
| Ranges library, range concepts | C++20 | [Lesson 11.3](../week11/lesson03.md) |
| Views: `filter`, `transform`, `take`, `drop`, `reverse`, `iota`, `split`, `join`, `keys/values/elements` | C++20 | [Lesson 11.3](../week11/lesson03.md) |
| Pipe syntax `|` | C++20 | [Lesson 11.3](../week11/lesson03.md) |
| Lazy evaluation | C++20 | [Lesson 11.3](../week11/lesson03.md) |
| `std::ranges::to` | C++23 | [Lesson 11.3](../week11/lesson03.md) |
| C++23 views: `zip`, `enumerate`, `chunk`, `slide`, `stride`, `cartesian_product`, `adjacent`, `join_with` | C++23 | [Lesson 11.3](../week11/lesson03.md) |
| Dangling protection (`std::ranges::dangling`) | C++20 | [Lesson 11.3](../week11/lesson03.md) |
| Borrowed ranges | C++20 | [Lesson 11.3](../week11/lesson03.md) |
| `std::generator` | C++23 | [Lesson 11.5](../week11/lesson05.md) |
| `co_yield` in generators | C++20 | [Lesson 11.5](../week11/lesson05.md) |
| Generators as ranges (compose with views) | C++23 | [Lesson 11.5](../week11/lesson05.md) |
| Recursive generators (`elements_of`) | C++23 | [Lesson 11.5](../week11/lesson05.md) |

## Standard library: utilities

| Feature | Standard | Taught in |
|---|---|---|
| `std::pair`, `std::tuple`, `std::tie`, `std::get`, `std::tuple_cat` | C++98/11 | [Lesson 11.4](../week11/lesson04.md) |
| `std::apply`, `std::make_from_tuple` | C++17 | [Lesson 11.4](../week11/lesson04.md) |
| Function objects: `std::plus<>`, `std::less<>`, `std::ranges::less`, `std::identity` | C++98/14/20 | [Lesson 11.4](../week11/lesson04.md) |
| `std::not_fn` | C++17 | [Lesson 11.4](../week11/lesson04.md) |
| `std::exchange`, `std::swap`, `std::as_const`, `std::to_underlying` | C++14/17/23 | [Lesson 11.4](../week11/lesson04.md) |
| `std::integer_sequence` (recap) | C++14 | [Lesson 11.4](../week11/lesson04.md) |
| `std::ref`/`std::cref`, `std::reference_wrapper` | C++11 | [Lesson 11.4](../week11/lesson04.md) |
| `<random>`: engines, distributions, seeding | C++11 | [Lesson 12.7](../week12/lesson07.md) |
| `<regex>` | C++11 | [Lesson 12.7](../week12/lesson07.md) |
| `<cmath>` special functions, `<numbers>` constants | C++17/20 | [Lesson 12.7](../week12/lesson07.md) |
| `std::numeric_limits` | C++98 | [Lesson 12.7](../week12/lesson07.md) |
| `std::bitset` | C++98 | [Lesson 12.7](../week12/lesson07.md) |
| `std::source_location` | C++20 | [Lesson 12.7](../week12/lesson07.md) |
| `std::stacktrace` | C++23 | [Lesson 12.7](../week12/lesson07.md) |
| `<locale>` basics | C++98 | [Lesson 12.7](../week12/lesson07.md) |
| `std::hash` | C++11 | [Lesson 12.7](../week12/lesson07.md) |
| `<cstdint>` fixed-width types (recap) | C++11 | [Lesson 12.7](../week12/lesson07.md) |

## Memory management

| Feature | Standard | Taught in |
|---|---|---|
| `std::unique_ptr`, `std::make_unique` | C++11/14 | [Lesson 12.1](../week12/lesson01.md) |
| `unique_ptr<T[]>` | C++11 | [Lesson 12.1](../week12/lesson01.md) |
| Custom deleters (function objects, lambdas, function pointers) | C++11 | [Lesson 12.1](../week12/lesson01.md) |
| Ownership transfer via move; `release`, `reset`, `get` | C++11 | [Lesson 12.1](../week12/lesson01.md) |
| `std::make_unique_for_overwrite` | C++20 | [Lesson 12.1](../week12/lesson01.md) |
| `std::out_ptr`, `std::inout_ptr` | C++23 | [Lesson 12.1](../week12/lesson01.md) |
| Smart pointer parameter guidelines | — | [Lesson 12.1](../week12/lesson01.md) |
| `std::shared_ptr`, `std::make_shared` | C++11 | [Lesson 12.2](../week12/lesson02.md) |
| Control block and reference counts | C++11 | [Lesson 12.2](../week12/lesson02.md) |
| `std::weak_ptr`, `lock()`, breaking cycles | C++11 | [Lesson 12.2](../week12/lesson02.md) |
| `std::enable_shared_from_this` | C++11 | [Lesson 12.2](../week12/lesson02.md) |
| Aliasing constructor | C++11 | [Lesson 12.2](../week12/lesson02.md) |
| `std::atomic<std::shared_ptr>` | C++20 | [Lesson 12.2](../week12/lesson02.md) |
| `make_shared` for arrays | C++20 | [Lesson 12.2](../week12/lesson02.md) |
| Allocator model (`std::allocator`, `allocator_traits`) | C++98/11 | [Lesson 12.3](../week12/lesson03.md) |
| `std::pmr::memory_resource`, `polymorphic_allocator` | C++17 | [Lesson 12.3](../week12/lesson03.md) |
| `monotonic_buffer_resource`, `unsynchronized_pool_resource`, `synchronized_pool_resource` | C++17 | [Lesson 12.3](../week12/lesson03.md) |
| `std::pmr::vector`, `std::pmr::string` | C++17 | [Lesson 12.3](../week12/lesson03.md) |
| Custom `operator new`/`delete` overloads | C++98 | [Lesson 12.3](../week12/lesson03.md) |
| Aligned allocation (`align_val_t`) | C++17 | [Lesson 12.3](../week12/lesson03.md) |

## Standard library: text & I/O

| Feature | Standard | Taught in |
|---|---|---|
| `std::format`, format specifications | C++20 | [Lesson 12.4](../week12/lesson04.md) |
| `std::print`, `std::println` | C++23 | [Lesson 12.4](../week12/lesson04.md) |
| Custom `std::formatter` specializations | C++20 | [Lesson 12.4](../week12/lesson04.md) |
| Formatting ranges | C++23 | [Lesson 12.4](../week12/lesson04.md) |
| iostreams, manipulators, `std::stringstream` | C++98 | [Lesson 12.4](../week12/lesson04.md) |
| `std::from_chars` / `std::to_chars` | C++17 | [Lesson 12.4](../week12/lesson04.md) |
| `char8_t`, UTF-8 string literals | C++20 | [Lesson 12.4](../week12/lesson04.md) |
| `std::format` compile-time format string checks | C++20 | [Lesson 12.4](../week12/lesson04.md) |

## Standard library: files

| Feature | Standard | Taught in |
|---|---|---|
| `std::filesystem::path` operations | C++17 | [Lesson 12.5](../week12/lesson05.md) |
| `directory_iterator`, `recursive_directory_iterator` | C++17 | [Lesson 12.5](../week12/lesson05.md) |
| `create_directories`, `copy`, `rename`, `remove_all` | C++17 | [Lesson 12.5](../week12/lesson05.md) |
| `file_size`, `last_write_time`, `status`, `exists` | C++17 | [Lesson 12.5](../week12/lesson05.md) |
| Error handling: `filesystem_error` vs `error_code` overloads | C++17 | [Lesson 12.5](../week12/lesson05.md) |
| File I/O with `std::ifstream`/`ofstream`, binary mode | C++98 | [Lesson 12.5](../week12/lesson05.md) |

## Standard library: time

| Feature | Standard | Taught in |
|---|---|---|
| `duration`, `time_point`, `duration_cast` | C++11 | [Lesson 12.6](../week12/lesson06.md) |
| Clocks: `steady_clock`, `system_clock`, `high_resolution_clock` | C++11 | [Lesson 12.6](../week12/lesson06.md) |
| Duration literals (`ms`, `s`, `h`) | C++14 | [Lesson 12.6](../week12/lesson06.md) |
| `floor`, `ceil`, `round` for durations | C++17 | [Lesson 12.6](../week12/lesson06.md) |
| Calendar types: `year_month_day`, `weekday`, `sys_days` | C++20 | [Lesson 12.6](../week12/lesson06.md) |
| Time zones: `zoned_time`, `tzdb` | C++20 | [Lesson 12.6](../week12/lesson06.md) |
| Formatting chrono types with `std::format` | C++20 | [Lesson 12.6](../week12/lesson06.md) |

## Concurrency

| Feature | Standard | Taught in |
|---|---|---|
| `std::thread`, `join`, `detach` | C++11 | [Lesson 13.1](../week13/lesson01.md) |
| `std::jthread` (auto-joining) | C++20 | [Lesson 13.1](../week13/lesson01.md) |
| `std::stop_token`, `std::stop_source`, `std::stop_callback` | C++20 | [Lesson 13.1](../week13/lesson01.md) |
| `std::this_thread::sleep_for`, `yield`, `get_id` | C++11 | [Lesson 13.1](../week13/lesson01.md) |
| `std::thread::hardware_concurrency` | C++11 | [Lesson 13.1](../week13/lesson01.md) |
| Passing arguments to threads (copies, `std::ref`) | C++11 | [Lesson 13.1](../week13/lesson01.md) |
| Data races are undefined behaviour | C++11 | [Lesson 13.2](../week13/lesson02.md) |
| `std::mutex`, `std::recursive_mutex`, `std::timed_mutex` | C++11 | [Lesson 13.2](../week13/lesson02.md) |
| `std::lock_guard`, `std::unique_lock` | C++11 | [Lesson 13.2](../week13/lesson02.md) |
| `std::scoped_lock` (deadlock-free multi-lock) | C++17 | [Lesson 13.2](../week13/lesson02.md) |
| `std::shared_mutex`, `std::shared_lock` | C++14/17 | [Lesson 13.2](../week13/lesson02.md) |
| `std::call_once`, `std::once_flag` | C++11 | [Lesson 13.2](../week13/lesson02.md) |
| Thread-safe static local initialization | C++11 | [Lesson 13.2](../week13/lesson02.md) |
| `std::condition_variable`, `wait` with predicate | C++11 | [Lesson 13.3](../week13/lesson03.md) |
| Spurious wakeups and lost wakeups | C++11 | [Lesson 13.3](../week13/lesson03.md) |
| `std::condition_variable_any` with `stop_token` | C++20 | [Lesson 13.3](../week13/lesson03.md) |
| `notify_one` vs `notify_all` | C++11 | [Lesson 13.3](../week13/lesson03.md) |
| Producer–consumer pattern | — | [Lesson 13.3](../week13/lesson03.md) |
| `std::async` and launch policies | C++11 | [Lesson 13.4](../week13/lesson04.md) |
| `std::future`, `std::shared_future` | C++11 | [Lesson 13.4](../week13/lesson04.md) |
| `std::promise` | C++11 | [Lesson 13.4](../week13/lesson04.md) |
| `std::packaged_task` | C++11 | [Lesson 13.4](../week13/lesson04.md) |
| Exception propagation through futures | C++11 | [Lesson 13.4](../week13/lesson04.md) |
| `wait_for` and `future_status` | C++11 | [Lesson 13.4](../week13/lesson04.md) |
| `std::latch` | C++20 | [Lesson 13.5](../week13/lesson05.md) |
| `std::barrier` with completion function | C++20 | [Lesson 13.5](../week13/lesson05.md) |
| `std::counting_semaphore`, `std::binary_semaphore` | C++20 | [Lesson 13.5](../week13/lesson05.md) |
| `thread_local` storage duration | C++11 | [Lesson 13.5](../week13/lesson05.md) |
| Choosing a synchronization primitive | — | [Lesson 13.5](../week13/lesson05.md) |

## Concurrency: atomics

| Feature | Standard | Taught in |
|---|---|---|
| `std::atomic<T>`, `load`, `store`, `exchange`, `fetch_add` | C++11 | [Lesson 14.1](../week14/lesson01.md) |
| `compare_exchange_weak` / `_strong` | C++11 | [Lesson 14.1](../week14/lesson01.md) |
| Memory orders: `seq_cst`, `acquire`, `release`, `acq_rel`, `relaxed` | C++11 | [Lesson 14.1](../week14/lesson01.md) |
| Happens-before and synchronizes-with | C++11 | [Lesson 14.1](../week14/lesson01.md) |
| `std::atomic_ref` | C++20 | [Lesson 14.1](../week14/lesson01.md) |
| `atomic::wait` / `notify_one` / `notify_all` | C++20 | [Lesson 14.1](../week14/lesson01.md) |
| `std::atomic_flag`, `is_lock_free`, `is_always_lock_free` | C++11/17 | [Lesson 14.1](../week14/lesson01.md) |
| `std::atomic<std::shared_ptr<T>>`, `atomic<float>` arithmetic | C++20 | [Lesson 14.1](../week14/lesson01.md) |
| `volatile` is not for threads | — | [Lesson 14.1](../week14/lesson01.md) |

## Concurrency: lock-free

| Feature | Standard | Taught in |
|---|---|---|
| Lock-free vs wait-free vs obstruction-free | — | [Lesson 14.2](../week14/lesson02.md) |
| SPSC ring buffer with acquire/release indices | C++11 | [Lesson 14.2](../week14/lesson02.md) |
| `std::hardware_destructive_interference_size` and false sharing | C++17 | [Lesson 14.2](../week14/lesson02.md) |
| `alignas` for cache-line separation | C++11 | [Lesson 14.2](../week14/lesson02.md) |
| The ABA problem (concept) | — | [Lesson 14.2](../week14/lesson02.md) |

## Concurrency: patterns

| Feature | Standard | Taught in |
|---|---|---|
| Thread pool design: work queue, workers, shutdown | — | [Lesson 14.3](../week14/lesson03.md) |
| Returning results with `std::packaged_task` + `std::future` | C++11 | [Lesson 14.3](../week14/lesson03.md) |
| Type-erased tasks (`std::function` / move-only wrappers) | C++11/23 | [Lesson 14.3](../week14/lesson03.md) |
| Graceful shutdown and exception safety | — | [Lesson 14.3](../week14/lesson03.md) |
| Work stealing (concept) | — | [Lesson 14.3](../week14/lesson03.md) |

## Concurrency: parallel algorithms

| Feature | Standard | Taught in |
|---|---|---|
| Execution policies: `seq`, `par`, `par_unseq`, `unseq` | C++17/20 | [Lesson 14.4](../week14/lesson04.md) |
| `std::reduce`, `std::transform_reduce` with policies | C++17 | [Lesson 14.4](../week14/lesson04.md) |
| Requirements: no data races, no locks in `par_unseq` | C++17 | [Lesson 14.4](../week14/lesson04.md) |
| Implementation notes (TBB for libstdc++) | — | [Lesson 14.4](../week14/lesson04.md) |
| `std::execution` senders/receivers (preview) | C++26 | [Lesson 14.4](../week14/lesson04.md) |

## Coroutines

| Feature | Standard | Taught in |
|---|---|---|
| `co_yield`, `co_return`, `co_await` | C++20 | [Lesson 14.5](../week14/lesson05.md) |
| Coroutine frame, `promise_type` | C++20 | [Lesson 14.5](../week14/lesson05.md) |
| `std::coroutine_handle` | C++20 | [Lesson 14.5](../week14/lesson05.md) |
| `initial_suspend` / `final_suspend` | C++20 | [Lesson 14.5](../week14/lesson05.md) |
| `std::suspend_always` / `suspend_never` | C++20 | [Lesson 14.5](../week14/lesson05.md) |
| Writing a generator by hand | C++20 | [Lesson 14.5](../week14/lesson05.md) |
| `std::generator` (recap) | C++23 | [Lesson 14.5](../week14/lesson05.md) |
| Awaitable protocol: `await_ready`, `await_suspend`, `await_resume` | C++20 | [Lesson 14.6](../week14/lesson06.md) |
| A lazy `Task<T>` type with continuations | C++20 | [Lesson 14.6](../week14/lesson06.md) |
| Symmetric transfer (returning a handle from `await_suspend`) | C++20 | [Lesson 14.6](../week14/lesson06.md) |
| Scheduling coroutines on an event loop | C++20 | [Lesson 14.6](../week14/lesson06.md) |
| Coroutine libraries (cppcoro, libunifex, Asio, stdexec) | — | [Lesson 14.6](../week14/lesson06.md) |

## Tooling: builds

| Feature | Standard | Taught in |
|---|---|---|
| Translation units, headers, include guards, `#pragma once` | C++98 | [Lesson 15.1](../week15/lesson01.md) |
| Modern CMake: targets, `target_link_libraries`, `target_compile_features` | — | [Lesson 15.1](../week15/lesson01.md) |
| Package managers: vcpkg, Conan; `find_package`, `FetchContent` | — | [Lesson 15.1](../week15/lesson01.md) |
| C++20 modules: `export module`, `import`, module partitions | C++20 | [Lesson 15.1](../week15/lesson01.md) |
| `import std;` standard library module | C++23 | [Lesson 15.1](../week15/lesson01.md) |
| Header units | C++20 | [Lesson 15.1](../week15/lesson01.md) |
| `__has_include`, feature-test macros (`__cpp_lib_*`) | C++17/20 | [Lesson 15.1](../week15/lesson01.md) |

## Tooling: linking & ABI

| Feature | Standard | Taught in |
|---|---|---|
| Compilation vs linking; object files and symbols | — | [Lesson 15.2](../week15/lesson02.md) |
| One Definition Rule (ODR) and its violations | C++98 | [Lesson 15.2](../week15/lesson02.md) |
| `inline` functions and `inline` variables | C++98/17 | [Lesson 15.2](../week15/lesson02.md) |
| Internal linkage: `static`, anonymous namespaces | C++98/11 | [Lesson 15.2](../week15/lesson02.md) |
| Name mangling and `extern "C"` | C++98 | [Lesson 15.2](../week15/lesson02.md) |
| Static vs shared libraries, symbol visibility | — | [Lesson 15.2](../week15/lesson02.md) |
| ABI stability (`std::string` C++11 ABI change, pimpl) | — | [Lesson 15.2](../week15/lesson02.md) |

## Tooling: quality

| Feature | Standard | Taught in |
|---|---|---|
| Unit testing frameworks: GoogleTest, Catch2, doctest | — | [Lesson 15.3](../week15/lesson03.md) |
| Test design: arrange–act–assert, edge cases, property tests | — | [Lesson 15.3](../week15/lesson03.md) |
| Sanitizers: ASan, UBSan, TSan, MSan, LSan | — | [Lesson 15.3](../week15/lesson03.md) |
| `static_assert` as compile-time tests | C++11 | [Lesson 15.3](../week15/lesson03.md) |
| clang-tidy, cppcheck, compiler warnings as errors | — | [Lesson 15.3](../week15/lesson03.md) |
| clang-format | — | [Lesson 15.3](../week15/lesson03.md) |
| Fuzzing with libFuzzer | — | [Lesson 15.3](../week15/lesson03.md) |
| Code coverage (gcov/llvm-cov) | — | [Lesson 15.3](../week15/lesson03.md) |

## Tooling: performance

| Feature | Standard | Taught in |
|---|---|---|
| Debuggers: gdb/lldb, breakpoints, watchpoints, core dumps | — | [Lesson 15.4](../week15/lesson04.md) |
| Optimization levels `-O0`…`-O3`, `-Os`, `-march=native` | — | [Lesson 15.4](../week15/lesson04.md) |
| Link-time optimization (LTO), profile-guided optimization (PGO) | — | [Lesson 15.4](../week15/lesson04.md) |
| Profilers: perf, VTune, Instruments, Tracy | — | [Lesson 15.4](../week15/lesson04.md) |
| Benchmarking pitfalls; Google Benchmark | — | [Lesson 15.4](../week15/lesson04.md) |
| Auto-vectorization and SIMD intrinsics; `std::simd` (C++26) | — | [Lesson 15.4](../week15/lesson04.md) |
| `[[likely]]`, `[[unlikely]]`, `[[assume]]` | C++20/23 | [Lesson 15.4](../week15/lesson04.md) |

## Performance

| Feature | Standard | Taught in |
|---|---|---|
| Memory hierarchy and cache lines | — | [Lesson 15.5](../week15/lesson05.md) |
| Contiguous data and prefetching; `vector` vs `list` | — | [Lesson 15.5](../week15/lesson05.md) |
| Array of structs (AoS) vs struct of arrays (SoA) | — | [Lesson 15.5](../week15/lesson05.md) |
| Struct padding, `alignof`, member ordering | C++11 | [Lesson 15.5](../week15/lesson05.md) |
| Branch prediction and branchless code | — | [Lesson 15.5](../week15/lesson05.md) |
| Avoiding allocations: `reserve`, small-buffer optimization, arenas | — | [Lesson 15.5](../week15/lesson05.md) |
| Move semantics and copy elision in hot paths | C++11/17 | [Lesson 15.5](../week15/lesson05.md) |

## Safety & security

| Feature | Standard | Taught in |
|---|---|---|
| Memory-safety bug classes (buffer overflow, UAF, type confusion) | — | [Lesson 15.6](../week15/lesson06.md) |
| Hardened standard library modes (`_GLIBCXX_ASSERTIONS`, libc++ hardening) | — | [Lesson 15.6](../week15/lesson06.md) |
| Compiler hardening: `-D_FORTIFY_SOURCE`, `-fstack-protector-strong`, `-ftrivial-auto-var-init` | — | [Lesson 15.6](../week15/lesson06.md) |
| Bounds-checked access: `.at()`, `std::span` | C++11/20 | [Lesson 15.6](../week15/lesson06.md) |
| C++ Core Guidelines and the GSL (`gsl::not_null`, `gsl::narrow`) | — | [Lesson 15.6](../week15/lesson06.md) |
| Safe integer handling: `std::in_range`, `std::cmp_less` | C++20 | [Lesson 15.6](../week15/lesson06.md) |
| Erroneous behaviour for uninitialized reads | C++26 | [Lesson 15.6](../week15/lesson06.md) |

## Interop

| Feature | Standard | Taught in |
|---|---|---|
| Designing a C ABI wrapper around C++ (opaque handles) | — | [Lesson 16.1](../week16/lesson01.md) |
| Exceptions must not cross C boundaries | C++11 | [Lesson 16.1](../week16/lesson01.md) |
| Callbacks with `void*` user data | — | [Lesson 16.1](../week16/lesson01.md) |
| pybind11 / nanobind bindings | — | [Lesson 16.1](../week16/lesson01.md) |
| JNI and the Android NDK | — | [Lesson 16.1](../week16/lesson01.md) |
| Ownership across language boundaries | — | [Lesson 16.1](../week16/lesson01.md) |

## Embedded

| Feature | Standard | Taught in |
|---|---|---|
| Freestanding implementations; `-fno-exceptions`, `-fno-rtti` | — | [Lesson 16.2](../week16/lesson02.md) |
| Memory-mapped registers with `volatile` | C++98 | [Lesson 16.2](../week16/lesson02.md) |
| No dynamic allocation after init; static pools | — | [Lesson 16.2](../week16/lesson02.md) |
| Fixed-point arithmetic | — | [Lesson 16.2](../week16/lesson02.md) |
| `constexpr` lookup tables | C++11/20 | [Lesson 16.2](../week16/lesson02.md) |
| Interrupt-safe data sharing (atomics, critical sections) | C++11 | [Lesson 16.2](../week16/lesson02.md) |
| `std::bit_cast`, `<bit>` operations | C++20 | [Lesson 16.2](../week16/lesson02.md) |
| Deprecated compound `volatile` operations | C++20 | [Lesson 16.2](../week16/lesson02.md) |

## Design

| Feature | Standard | Taught in |
|---|---|---|
| Strategy via `std::function`, templates, or concepts | C++11/20 | [Lesson 16.3](../week16/lesson03.md) |
| Observer with lifetime safety (`weak_ptr` / tokens) | C++11 | [Lesson 16.3](../week16/lesson03.md) |
| Factory and registry | — | [Lesson 16.3](../week16/lesson03.md) |
| Visitor via `std::variant` + `std::visit` | C++17 | [Lesson 16.3](../week16/lesson03.md) |
| Pimpl idiom (recap) and type erasure (recap) | C++11 | [Lesson 16.3](../week16/lesson03.md) |
| RAII scope guards | C++11 | [Lesson 16.3](../week16/lesson03.md) |
| Policy-based design | C++98 | [Lesson 16.3](../week16/lesson03.md) |
| Strong types to prevent argument mix-ups | C++11 | [Lesson 16.4](../week16/lesson04.md) |
| `[[nodiscard]]` (with reason), `[[deprecated]]` | C++17/20 | [Lesson 16.4](../week16/lesson04.md) |
| Choosing an error-handling policy for a library | — | [Lesson 16.4](../week16/lesson04.md) |
| Const-correctness and value semantics in interfaces | C++98 | [Lesson 16.4](../week16/lesson04.md) |
| Inline namespaces for API versioning | C++11 | [Lesson 16.4](../week16/lesson04.md) |
| Header hygiene and minimal includes | — | [Lesson 16.4](../week16/lesson04.md) |
| Semantic versioning and ABI policy | — | [Lesson 16.4](../week16/lesson04.md) |

## C++26 preview

| Feature | Standard | Taught in |
|---|---|---|
| Static reflection (`^^T`, `std::meta`, splicers) | C++26 (preview) | [Lesson 16.5](../week16/lesson05.md) |
| Contracts: `pre`, `post`, `contract_assert` | C++26 (preview) | [Lesson 16.5](../week16/lesson05.md) |
| `std::execution` senders/receivers | C++26 (preview) | [Lesson 16.5](../week16/lesson05.md) |
| `std::inplace_vector` | C++26 (preview) | [Lesson 16.5](../week16/lesson05.md) |
| Pack indexing `Ts...[N]` | C++26 (preview) | [Lesson 16.5](../week16/lesson05.md) |
| `= delete("reason")` | C++26 (preview) | [Lesson 16.5](../week16/lesson05.md) |
| Placeholder variables `_` | C++26 (preview) | [Lesson 16.5](../week16/lesson05.md) |
| `#embed` | C++26 (preview) | [Lesson 16.5](../week16/lesson05.md) |
| `std::simd`, `std::hazard_pointer`, `std::rcu` | C++26 (preview) | [Lesson 16.5](../week16/lesson05.md) |
| Erroneous behaviour; hardened standard library | C++26 (preview) | [Lesson 16.5](../week16/lesson05.md) |

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
