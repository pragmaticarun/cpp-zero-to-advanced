WEEK = dict(num=15, title="Building, testing, and performance engineering", intro="""
Writing correct C++ is half the job. The other half is building it reliably, proving it works, finding out
why it's slow, and keeping it secure. This week is about the tools and habits that professional C++ teams
rely on: CMake and modules, linking and ABI, tests and sanitizers, profilers, cache-aware design, and
hardening.
""", lessons=[
dict(title="Build systems: CMake, packages, and C++20 modules", std="C++20", minutes=13, area="Tooling: builds",
features=[("Translation units, headers, include guards, `#pragma once`", "C++98"), ("Modern CMake: targets, `target_link_libraries`, `target_compile_features`", "—"), ("Package managers: vcpkg, Conan; `find_package`, `FetchContent`", "—"), ("C++20 modules: `export module`, `import`, module partitions", "C++20"), ("`import std;` standard library module", "C++23"), ("Header units", "C++20"), ("`__has_include`, feature-test macros (`__cpp_lib_*`)", "C++17/20")],
why="""
Your project grows from one file to fifty, plus three libraries. Compiling by hand stops scaling the first
day. CMake is the de facto standard C++ build generator, and C++20 modules are the first real fix for
C++'s 50-year-old textual `#include` model, which re-parses the same headers thousands of times.
""",
body="""
## Modern CMake: think in targets

```cmake
cmake_minimum_required(VERSION 3.28)
project(mixer LANGUAGES CXX)

add_library(dsp src/gain.cpp src/filter.cpp)
target_include_directories(dsp PUBLIC include)
target_compile_features(dsp PUBLIC cxx_std_20)
target_compile_options(dsp PRIVATE -Wall -Wextra -Wpedantic)

add_executable(mixer src/main.cpp)
target_link_libraries(mixer PRIVATE dsp)

include(FetchContent)
FetchContent_Declare(Catch2 GIT_REPOSITORY https://github.com/catchorg/Catch2.git GIT_TAG v3.5.2)
FetchContent_MakeAvailable(Catch2)
add_executable(tests tests/test_gain.cpp)
target_link_libraries(tests PRIVATE dsp Catch2::Catch2WithMain)
enable_testing()
add_test(NAME tests COMMAND tests)
```

`PUBLIC`/`PRIVATE`/`INTERFACE` say whether a usage requirement propagates to dependents. Avoid global
`include_directories` / `CMAKE_CXX_FLAGS` — set properties on targets. Build out of source:
`cmake -S . -B build -G Ninja && cmake --build build && ctest --test-dir build`.

## Modules (C++20)

```cpp
// gain.cppm
export module dsp.gain;
export double apply_gain(double x, double g) { return x * g; }
// main.cpp
import dsp.gain;
import std;            // C++23: the whole standard library as one module
```

Modules are compiled once into a binary interface, don't leak macros, and make the interface explicit
(`export`). Honest status (2026): MSVC, Clang ≥ 17 and GCC ≥ 14 support them, and CMake ≥ 3.28 handles
dependency scanning with Ninja — but tooling (IDEs, package managers) is still catching up, so many
codebases still use headers. Our checker compiles single files, so modules are shown here, not compiled.

## Portable feature detection

When code must work across compilers, test feature-test macros rather than compiler versions:

{{ex}}
""",
files={"": r'''
#include <iostream>
#include <version>          // defines all __cpp_lib_* macros

#if __has_include(<expected>)
#include <expected>
#endif

int main() {
#ifdef __cpp_lib_expected
    std::cout << "std::expected available (" << __cpp_lib_expected << ")\n";
#else
    std::cout << "std::expected not available in this mode\n";
#endif
#ifdef __cpp_concepts
    std::cout << "concepts: yes\n";
#endif
    std::cout << "__cplusplus = " << (__cplusplus >= 202002L ? ">= C++20" : "< C++20") << '\n';
}
'''},
takeaways=["Modern CMake is target-based: set includes, features and links on targets with PUBLIC/PRIVATE.",
"Use FetchContent or a package manager (vcpkg, Conan) for dependencies.",
"Modules replace textual inclusion with compiled interfaces; tooling support is maturing.",
"Use `<version>` feature-test macros for portability, not compiler-version checks."],
quiz=[("What does `PUBLIC` mean in `target_include_directories(dsp PUBLIC include)`?", "The include directory is used to build `dsp` *and* propagates to targets that link `dsp`."),
("Name two advantages of modules over headers.", "Faster builds (parsed once), no macro leakage, explicit export control, less ODR fragility."),
("Why prefer `#ifdef __cpp_lib_expected` over checking GCC's version?", "It checks the actual feature, works across compilers and standard libraries, and handles `-std` modes.")]),

dict(title="Linking, the ODR, ABI, and extern \"C\"", std="C++20", minutes=12, area="Tooling: linking & ABI",
features=[("Compilation vs linking; object files and symbols", "—"), ("One Definition Rule (ODR) and its violations", "C++98"), ("`inline` functions and `inline` variables", "C++98/17"), ("Internal linkage: `static`, anonymous namespaces", "C++98/11"), ("Name mangling and `extern \"C\"`", "C++98"), ("Static vs shared libraries, symbol visibility", "—"), ("ABI stability (`std::string` C++11 ABI change, pimpl)", "—")],
why="""
"undefined reference to `mixer::Gain::apply(double)`" — every C++ programmer meets the linker the hard way.
Understanding what the compiler hands to the linker explains these errors, the One Definition Rule, why C
libraries need `extern "C"`, and why changing a private member can break binaries that use your library.
""",
body="""
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

{{ex}}

## ABI

The **ABI** is the binary contract: object layout, calling conventions, mangling, vtable layout. Adding a
private data member changes `sizeof` and breaks every binary compiled against the old header. Libraries that
need stability use the **pimpl** idiom (Week 5) or a C API. (GCC's switch to a C++11-conforming
`std::string` in 2015 required a dual ABI — that's how costly ABI breaks are.)
""",
files={"": r'''
#include <cstdio>
#include <cstring>
#include <iostream>

// What a C header would declare; extern "C" disables mangling so C code can link to it
extern "C" {
    int mixer_version(void);
    double mixer_apply_gain(double sample, double gain);
}

namespace {                                    // internal linkage: invisible to other TUs
int helper_calls = 0;
double clamp1(double x) { ++helper_calls; return x > 1.0 ? 1.0 : (x < -1.0 ? -1.0 : x); }
}

extern "C" int mixer_version(void) { return 3; }
extern "C" double mixer_apply_gain(double sample, double gain) { return clamp1(sample * gain); }

inline constexpr int kMaxChannels = 32;        // C++17 inline variable: safe to define in a header

int compare_ints(const void* a, const void* b) {
    int x = *static_cast<const int*>(a), y = *static_cast<const int*>(b);
    return (x > y) - (x < y);
}

int main() {
    std::cout << "C API version " << mixer_version() << ", gain(0.8, 2) = " << mixer_apply_gain(0.8, 2.0) << '\n';
    int v[] = {5, 2, 9, 1};
    std::qsort(v, 4, sizeof(int), compare_ints);  // a C library calling back into C++
    for (int x : v) std::cout << x << ' ';
    std::cout << "\nhelper calls: " << helper_calls << ", max channels " << kMaxChannels << '\n';
}
'''},
takeaways=["Undefined reference = missing definition in the link; multiple definition = defined twice.",
"The ODR requires identical definitions across TUs; violations are silent UB.",
"Use anonymous namespaces for TU-local helpers and `inline` for header definitions.",
"`extern \"C\"` disables mangling for C interop; pimpl or C APIs preserve ABI stability."],
quiz=[("Why can't C code call an overloaded C++ function directly?", "C++ mangles parameter types into symbol names; C expects plain names. Use `extern \"C\"` wrappers (which can't be overloaded)."),
("Is adding a private member to a class in a shared library's header ABI-compatible?", "No — it changes the object's size/layout, breaking binaries compiled against the old header."),
("How do you define a global constant in a header without ODR problems?", "`inline constexpr` (C++17 inline variable) — or `constexpr` at namespace scope, which has internal linkage.")]),

dict(title="Testing, sanitizers, and static analysis", std="C++20", minutes=13, area="Tooling: quality",
features=[("Unit testing frameworks: GoogleTest, Catch2, doctest", "—"), ("Test design: arrange–act–assert, edge cases, property tests", "—"), ("Sanitizers: ASan, UBSan, TSan, MSan, LSan", "—"), ("`static_assert` as compile-time tests", "C++11"), ("clang-tidy, cppcheck, compiler warnings as errors", "—"), ("clang-format", "—"), ("Fuzzing with libFuzzer", "—"), ("Code coverage (gcov/llvm-cov)", "—")],
why="""
In C++, a bug can sit silently for months — reading freed memory "works" until a different allocator
layout makes it crash in production. The defence is layered: tests prove behaviour, sanitizers catch UB
while the tests run, static analysis finds bugs without running anything, and fuzzing finds inputs you
didn't think of. This course's own CI does exactly this for every example.
""",
body="""
## Unit tests

Frameworks (GoogleTest, Catch2, doctest) give you assertions, fixtures and test discovery. The core idea
fits in a few lines — here's a tiny self-contained harness so the example compiles on its own:

{{ex}}

With Catch2 the same test is `TEST_CASE("ring wraps") { ... REQUIRE(r.size() == 2); }`.

Test **edge cases** (empty, one element, full, wrap-around, max values), not just the happy path. A
**property test** checks an invariant over many random inputs (e.g. "pushing then popping N items returns
them in order").

## Sanitizers: run your tests under them

| Sanitizer | Flag | Finds |
|---|---|---|
| AddressSanitizer | `-fsanitize=address` | out-of-bounds, use-after-free, leaks (with LSan) |
| UndefinedBehaviorSanitizer | `-fsanitize=undefined` | signed overflow, bad shifts, misaligned access, null deref |
| ThreadSanitizer | `-fsanitize=thread` | data races, some deadlocks |
| MemorySanitizer (Clang) | `-fsanitize=memory` | reads of uninitialized memory |

Cost: roughly 2× (ASan) to 5–15× (TSan) slowdown. Run them in CI on every commit, not just when hunting.

## Static analysis and formatting

- Compile with `-Wall -Wextra -Wpedantic -Werror` (and `-Wconversion -Wshadow` for new code).
- **clang-tidy** with `cppcoreguidelines-*`, `bugprone-*`, `modernize-*` checks.
- **cppcheck** as a second opinion.
- **clang-format** with a committed `.clang-format` ends style debates.

## Fuzzing

libFuzzer calls `extern "C" int LLVMFuzzerTestOneInput(const uint8_t*, size_t)` millions of times with
mutated inputs, under ASan/UBSan. Any parser that reads untrusted data should be fuzzed.
""",
files={"": r'''
#include <array>
#include <cstddef>
#include <functional>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// --- a tiny test harness (real projects: GoogleTest / Catch2 / doctest) ---
struct TestCase { std::string name; std::function<void()> fn; };
std::vector<TestCase>& registry() { static std::vector<TestCase> r; return r; }
int failures = 0;
#define CHECK(cond) do { if (!(cond)) { ++failures; std::cout << "  FAILED: " #cond " (line " << __LINE__ << ")\n"; } } while (0)
struct Register { Register(std::string n, std::function<void()> f) { registry().push_back({std::move(n), std::move(f)}); } };

// --- code under test ---
template <typename T, std::size_t N>
class Ring {
public:
    bool push(T v) { if (size_ == N) return false; data_[(head_ + size_++) % N] = v; return true; }
    bool pop(T& out) { if (size_ == 0) return false; out = data_[head_]; head_ = (head_ + 1) % N; --size_; return true; }
    std::size_t size() const { return size_; }
private:
    std::array<T, N> data_{};
    std::size_t head_ = 0, size_ = 0;
};

static_assert(sizeof(Ring<char, 4>) >= 4, "compile-time tests are free");

Register t1{"empty ring pops nothing", [] { Ring<int, 3> r; int x; CHECK(!r.pop(x)); CHECK(r.size() == 0); }};
Register t2{"full ring rejects push", [] { Ring<int, 2> r; CHECK(r.push(1)); CHECK(r.push(2)); CHECK(!r.push(3)); }};
Register t3{"wrap-around keeps order", [] {
    Ring<int, 3> r; int x = 0;
    r.push(1); r.push(2); r.pop(x); r.push(3); r.push(4);
    r.pop(x); CHECK(x == 2); r.pop(x); CHECK(x == 3); r.pop(x); CHECK(x == 4);
}};
Register t4{"property: FIFO for random sequences", [] {
    std::mt19937 rng{7};
    for (int trial = 0; trial < 200; ++trial) {
        Ring<int, 8> r; std::vector<int> model; int next = 0;
        for (int step = 0; step < 50; ++step) {
            if (rng() % 2) { if (r.push(next)) model.push_back(next); ++next; }
            else { int x; bool ok = r.pop(x); CHECK(ok == !model.empty()); if (ok) { CHECK(x == model.front()); model.erase(model.begin()); } }
        }
        CHECK(r.size() == model.size());
    }
}};

int main() {
    for (auto& t : registry()) { std::cout << "[ RUN ] " << t.name << '\n'; t.fn(); }
    std::cout << registry().size() << " tests, " << failures << " failures\n";
    return failures == 0 ? 0 : 1;
}
''', "san": ["address", "undefined"]},
takeaways=["Test edge cases and invariants (property tests), not only happy paths.",
"Run tests under ASan+UBSan and TSan in CI on every commit.",
"Warnings-as-errors, clang-tidy and cppcheck catch bugs before running.",
"Fuzz any code that parses untrusted input."],
quiz=[("Which sanitizer finds a data race?", "ThreadSanitizer (`-fsanitize=thread`)."),
("Can ASan and TSan be combined in one build?", "No — they're incompatible; use separate builds."),
("What's a property-based test?", "A test that checks an invariant holds across many generated inputs, often against a simple reference model.")]),

dict(title="Debugging, profiling, and compiler optimization", std="C++20", minutes=12, area="Tooling: performance",
features=[("Debuggers: gdb/lldb, breakpoints, watchpoints, core dumps", "—"), ("Optimization levels `-O0`…`-O3`, `-Os`, `-march=native`", "—"), ("Link-time optimization (LTO), profile-guided optimization (PGO)", "—"), ("Profilers: perf, VTune, Instruments, Tracy", "—"), ("Benchmarking pitfalls; Google Benchmark", "—"), ("Auto-vectorization and SIMD intrinsics; `std::simd` (C++26)", "—"), ("`[[likely]]`, `[[unlikely]]`, `[[assume]]`", "C++20/23")],
why="""
"It's slow" is not a diagnosis. Professionals measure first: profile to find the 5% of code that takes 90%
of the time, then optimize *that*, then measure again. And when it crashes, a debugger beats a hundred
`std::cout` lines. This lesson is a field guide to the tools.
""",
body="""
## Debugging essentials

Build with `-g -O0` (or `-Og`) for debugging. In gdb/lldb: `break file.cpp:42`, `run`, `bt` (backtrace),
`frame 2`, `print x`, `watch buffer[3]` (stop when memory changes), `catch throw`. Enable core dumps
(`ulimit -c unlimited`) to inspect crashes after the fact.

## Optimization flags

`-O2` is the usual release level; `-O3` adds aggressive inlining/vectorization (measure — not always
faster). `-march=native` uses your CPU's instructions (don't ship it to unknown machines). **LTO** (`-flto`)
optimizes across translation units; **PGO** (`-fprofile-generate` → run → `-fprofile-use`) lets the compiler
optimize for real workloads — often 10–20% for branchy code.

## Profiling

Sampling profilers (`perf record -g ./app && perf report`, VTune, Instruments) show where time goes with
low overhead. Frame profilers like Tracy are great for games and real-time code.

## Micro-benchmarks lie unless you're careful

The compiler deletes work whose result is unused; caches are warm on the second run; timers have
resolution limits. Use Google Benchmark (`benchmark::DoNotOptimize`), repeat runs, and report medians.

{{ex}}

The example measures a summation two ways and is careful to *use* the result. Timings are machine-dependent,
so only the checksum is verified.

## Hints to the compiler

`[[likely]]`/`[[unlikely]]` (C++20) mark branch probabilities; `[[assume(expr)]]` (C++23) promises a
condition (UB if false!). C++26 adds `std::simd` for portable data-parallel types. Use hints only after
profiling shows they help.
""",
files={"": r'''
#include <chrono>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <vector>

template <typename F>
double time_ms(F&& f, int reps) {
    auto best = std::chrono::duration<double, std::milli>::max();
    for (int r = 0; r < reps; ++r) {                    // take the best of several runs
        auto t0 = std::chrono::steady_clock::now();
        f();
        auto dt = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0);
        if (dt < best) best = dt;
    }
    return best.count();
}

int classify(int x) {
    if (x < 0) [[unlikely]] return -1;
    return x % 3;
}

int main() {
    std::vector<std::int32_t> data(2'000'000);
    std::iota(data.begin(), data.end(), 0);
    volatile std::int64_t sink = 0;                     // keep results observable so work isn't deleted

    double loop_ms = time_ms([&] {
        std::int64_t s = 0;
        for (std::size_t i = 0; i < data.size(); ++i) s += data[i];
        sink = s;
    }, 5);
    double accum_ms = time_ms([&] { sink = std::accumulate(data.begin(), data.end(), std::int64_t{0}); }, 5);

    std::cout << "checksum " << sink << '\n';
    std::cout << "classify(-5)=" << classify(-5) << " classify(7)=" << classify(7) << '\n';
    std::cerr << "loop " << loop_ms << " ms, accumulate " << accum_ms << " ms (machine-dependent)\n";
}
'''},
takeaways=["Measure before optimizing: sampling profilers find the hot spots.",
"`-O2` for release; LTO and PGO give cross-TU and workload-driven gains.",
"Benchmarks must defeat dead-code elimination, warm caches deliberately and repeat runs.",
"Use `[[likely]]`/`[[assume]]` sparingly and only with evidence."],
quiz=[("Why might a benchmark of `for (...) s += x;` report 0 ns?", "If `s` is unused the optimizer removes the loop entirely."),
("What does PGO do?", "Uses profiles from representative runs to guide inlining, layout and branch decisions."),
("What happens if an `[[assume(x > 0)]]` is false at run time?", "Undefined behaviour — the compiler may have optimized based on it.")]),

dict(title="Performance: caches, memory layout, and data-oriented design", std="C++20", minutes=13, area="Performance",
features=[("Memory hierarchy and cache lines", "—"), ("Contiguous data and prefetching; `vector` vs `list`", "—"), ("Array of structs (AoS) vs struct of arrays (SoA)", "—"), ("Struct padding, `alignof`, member ordering", "C++11"), ("Branch prediction and branchless code", "—"), ("Avoiding allocations: `reserve`, small-buffer optimization, arenas", "—"), ("Move semantics and copy elision in hot paths", "C++11/17")],
why="""
A main-memory access costs ~100 ns; an L1 cache hit ~1 ns. On modern hardware, *how your data is laid out*
often matters more than the algorithm's big-O constant. Data-oriented design — organizing data for the way
it's accessed — routinely gives 2–10× speedups in games, audio and simulation code.
""",
body="""
## The rules of thumb

1. **Contiguous beats linked**: `std::vector` iterates at memory bandwidth; `std::list` chases pointers and
   misses cache on every node.
2. **Only load what you use**: if a loop touches one field of a 64-byte struct, you load 64 bytes to use 4.
3. **Avoid allocations in hot loops**: `reserve`, reuse buffers, use arenas (Week 12).
4. **Predictable branches are cheap; unpredictable ones cost ~15 cycles** each.

## AoS vs SoA

```cpp
struct Particle { float x, y, z, vx, vy, vz; std::uint32_t color; bool alive; };   // AoS
struct Particles { std::vector<float> x, y, z, vx, vy, vz; ... };                  // SoA
```

Updating positions in SoA streams through tightly packed arrays (and vectorizes); AoS drags the unused
fields through the cache.

{{ex}}

The example also shows **padding**: member order changes `sizeof`. Timings print to stderr since they're
machine-dependent; on typical hardware SoA and vector traversal are several times faster.

!!! tip "Pro tip"
    Don't restructure everything into SoA. Do it for the hot data that profiling identifies. Clear code first,
    then optimize with evidence.
""",
files={"": r'''
#include <chrono>
#include <cstdint>
#include <iostream>
#include <list>
#include <numeric>
#include <vector>

struct Padded { char a; double b; char c; };          // 1 + 7 pad + 8 + 1 + 7 pad = 24
struct Reordered { double b; char a; char c; };        // 8 + 1 + 1 + 6 pad = 16

struct ParticleAoS { float x, y, z, vx, vy, vz; std::uint32_t color; bool alive; float mass, age; };
struct ParticlesSoA { std::vector<float> x, vx; };

template <typename F> double ms(F f) {
    auto t0 = std::chrono::steady_clock::now(); f();
    return std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
}

int main() {
    std::cout << "sizeof Padded=" << sizeof(Padded) << " Reordered=" << sizeof(Reordered) << '\n';

    constexpr std::size_t n = 1'000'000;
    std::vector<ParticleAoS> aos(n, ParticleAoS{0, 0, 0, 1, 0, 0, 0, true, 1, 0});
    ParticlesSoA soa{std::vector<float>(n, 0.0f), std::vector<float>(n, 1.0f)};

    double t_aos = ms([&] { for (auto& p : aos) p.x += p.vx * 0.5f; });
    double t_soa = ms([&] { for (std::size_t i = 0; i < n; ++i) soa.x[i] += soa.vx[i] * 0.5f; });
    std::cout << "positions equal: " << std::boolalpha << (aos[n / 2].x == soa.x[n / 2]) << '\n';

    std::vector<int> v(n, 1);
    std::list<int> l(n, 1);
    long long sv = 0, sl = 0;
    double t_vec = ms([&] { sv = std::accumulate(v.begin(), v.end(), 0LL); });
    double t_list = ms([&] { sl = std::accumulate(l.begin(), l.end(), 0LL); });
    std::cout << "sums " << sv << ' ' << sl << '\n';
    std::cerr << "AoS " << t_aos << " ms, SoA " << t_soa << " ms; vector " << t_vec << " ms, list " << t_list << " ms\n";
}
'''},
takeaways=["Memory access patterns often dominate performance; keep hot data contiguous.",
"SoA layouts stream only the fields a loop uses and vectorize well.",
"Order members largest-to-smallest to reduce padding.",
"Optimize the hot path identified by profiling, not everything."],
quiz=[("Why is iterating a `std::list` slower than a `std::vector` of the same size?", "List nodes are scattered in memory, so each step is a likely cache miss; vector elements are contiguous and prefetched."),
("What is `sizeof(struct { char a; double b; char c; })` on a typical 64-bit ABI?", "24 bytes due to padding for 8-byte alignment of `double`."),
("When does SoA beat AoS?", "When hot loops access only a few fields of many objects.")]),

dict(title="Security hardening and the C++ Core Guidelines", std="C++20", minutes=12, area="Safety & security",
features=[("Memory-safety bug classes (buffer overflow, UAF, type confusion)", "—"), ("Hardened standard library modes (`_GLIBCXX_ASSERTIONS`, libc++ hardening)", "—"), ("Compiler hardening: `-D_FORTIFY_SOURCE`, `-fstack-protector-strong`, `-ftrivial-auto-var-init`", "—"), ("Bounds-checked access: `.at()`, `std::span`", "C++11/20"), ("C++ Core Guidelines and the GSL (`gsl::not_null`, `gsl::narrow`)", "—"), ("Safe integer handling: `std::in_range`, `std::cmp_less`", "C++20"), ("Erroneous behaviour for uninitialized reads", "C++26")],
why="""
Roughly 70% of serious security bugs in large C and C++ codebases are memory-safety bugs. Governments and
companies now ask hard questions about C++. The honest answer: modern C++ with good habits and hardened
builds eliminates most of these bugs — but only if you actually use them. This lesson collects the habits.
""",
body="""
## Habits that eliminate whole bug classes

| Bug class | Modern C++ habit |
|---|---|
| Buffer overflow | containers + `std::span`, range-for, hardened library checks |
| Use-after-free / leaks | RAII, smart pointers, no raw owning pointers |
| Dangling references | don't return references to locals; watch `string_view`/`span` lifetimes |
| Integer overflow / sign bugs | `std::cmp_less`, `std::in_range`, checked narrowing |
| Uninitialized memory | always initialize; `-ftrivial-auto-var-init=zero`; C++26 makes it *erroneous behaviour* |
| Type confusion | no C casts; `std::variant` over unions; `dynamic_cast` when downcasting |

## Hardened builds

- `-D_GLIBCXX_ASSERTIONS` (libstdc++) or `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST` (libc++)
  turns `operator[]` out-of-bounds and similar precondition violations into a trap. Cost is usually low
  single-digit percent; many vendors ship with it enabled.
- `-D_FORTIFY_SOURCE=3 -O2`, `-fstack-protector-strong`, `-fstack-clash-protection`, `-fPIE -pie`,
  `-Wl,-z,relro,-z,now` — see the OpenSSF compiler hardening guide.

{{ex}}

## The C++ Core Guidelines

The [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/) (Stroustrup & Sutter) are the
community's style and safety rulebook: R.* for resources, F.* for functions, ES.* for expressions, CP.* for
concurrency. The GSL library provides helpers like `gsl::not_null<T*>` and `gsl::narrow<T>` (throws on
lossy conversion). clang-tidy can enforce many rules automatically.
""",
files={"": r'''
#include <cstdint>
#include <iostream>
#include <limits>
#include <span>
#include <stdexcept>
#include <utility>
#include <vector>

template <typename To, typename From>
To narrow_checked(From v) {                            // like gsl::narrow
    if (!std::in_range<To>(v)) throw std::range_error{"narrowing would lose data"};
    return static_cast<To>(v);
}

double average(std::span<const double> xs) {          // pointer+length travel together
    if (xs.empty()) return 0.0;
    double s = 0;
    for (double x : xs) s += x;                        // no index arithmetic to get wrong
    return s / static_cast<double>(xs.size());
}

int main() {
    std::vector<double> levels{0.5, 0.25, 0.75};
    std::cout << "average " << average(levels) << '\n';
    try { (void)levels.at(10); } catch (const std::out_of_range&) { std::cout << "at() caught out-of-bounds\n"; }

    int count = -1;
    std::size_t size = 3;
    std::cout << std::boolalpha << "-1 < 3u with raw compare: " << (static_cast<unsigned>(count) < size)
              << ", with cmp_less: " << std::cmp_less(count, size) << '\n';
    try { (void)narrow_checked<std::uint8_t>(300); } catch (const std::range_error& e) { std::cout << e.what() << '\n'; }
    std::cout << "narrow 200 -> " << int{narrow_checked<std::uint8_t>(200)} << '\n';

    int initialized{};                                 // always initialize
    std::cout << "initialized = " << initialized << '\n';
}
''', "san": ["address", "undefined"]},
takeaways=["Most memory-safety bugs are prevented by RAII, containers, spans and no raw owning pointers.",
"Ship hardened builds: library assertions, FORTIFY_SOURCE, stack protector, PIE/RELRO.",
"Use `std::cmp_less`/`std::in_range` and checked narrowing for integer safety.",
"Follow the C++ Core Guidelines and enforce them with clang-tidy."],
quiz=[("What does `-D_GLIBCXX_ASSERTIONS` do?", "Enables libstdc++ precondition checks, e.g. trapping on out-of-bounds `vector::operator[]`."),
("Why is `-1 < 3u` false?", "-1 converts to a huge unsigned value; use `std::cmp_less(-1, 3u)` which compares mathematically."),
("Name three Core Guidelines-backed habits that prevent use-after-free.", "RAII ownership, smart pointers instead of raw owning pointers, not storing references/views that outlive their owner.")]),
],
assignment=dict(title="Harden and test a parser", task="""
Take a small key=value packet parser that reads lengths from untrusted bytes, write table-driven tests
including malicious inputs (truncated, oversized lengths, negative values), and make it safe using
`std::span`, `std::in_range` and `std::expected`. Run under ASan+UBSan. Bonus: write a libFuzzer entry point
(`LLVMFuzzerTestOneInput`) for it.
""", std="c++23", san=["address", "undefined"], solution=r'''
#include <cstdint>
#include <expected>
#include <iostream>
#include <span>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

enum class ParseError { truncated, too_long, empty_key };
std::string_view to_string(ParseError e) {
    switch (e) {
        case ParseError::truncated: return "truncated";
        case ParseError::too_long: return "too_long";
        case ParseError::empty_key: return "empty_key";
    }
    return "?";
}

using Field = std::pair<std::string, std::string>;

// Format: repeated [klen:u8][key bytes][vlen:u8][value bytes]
std::expected<std::vector<Field>, ParseError> parse(std::span<const std::uint8_t> in) {
    std::vector<Field> out;
    auto take = [&](std::size_t n) -> std::expected<std::span<const std::uint8_t>, ParseError> {
        if (n > in.size()) return std::unexpected{ParseError::truncated};
        auto s = in.first(n);
        in = in.subspan(n);
        return s;
    };
    while (!in.empty()) {
        auto klen = take(1); if (!klen) return std::unexpected{klen.error()};
        if ((*klen)[0] == 0) return std::unexpected{ParseError::empty_key};
        if ((*klen)[0] > 64) return std::unexpected{ParseError::too_long};
        auto key = take((*klen)[0]); if (!key) return std::unexpected{key.error()};
        auto vlen = take(1); if (!vlen) return std::unexpected{vlen.error()};
        auto val = take((*vlen)[0]); if (!val) return std::unexpected{val.error()};
        out.emplace_back(std::string(key->begin(), key->end()), std::string(val->begin(), val->end()));
    }
    return out;
}

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t* data, std::size_t size) {
    (void)parse({data, size});                     // must never crash, whatever the bytes
    return 0;
}

int main() {
    struct Case { const char* name; std::vector<std::uint8_t> bytes; };
    std::vector<Case> cases{
        {"valid", {4, 'r', 'a', 't', 'e', 5, '4', '8', '0', '0', '0', 2, 'c', 'h', 1, '2'}},
        {"empty input", {}},
        {"truncated key", {10, 'a', 'b'}},
        {"value length past end", {1, 'k', 200, 'v'}},
        {"zero-length key", {0, 1, 'x'}},
        {"oversized key", {200}},
    };
    for (const auto& c : cases) {
        auto r = parse(c.bytes);
        std::cout << c.name << ": ";
        if (r) { std::cout << r->size() << " field(s)"; for (auto& [k, v] : *r) std::cout << ' ' << k << '=' << v; }
        else std::cout << "error " << to_string(r.error());
        std::cout << '\n';
    }
    std::uint64_t state = 1;                         // mini fuzz loop: random bytes must never crash
    for (int i = 0; i < 2000; ++i) {
        std::vector<std::uint8_t> buf(state % 40);
        for (auto& b : buf) { state = state * 6364136223846793005ULL + 1442695040888963407ULL; b = static_cast<std::uint8_t>(state >> 56); }
        LLVMFuzzerTestOneInput(buf.data(), buf.size());
    }
    std::cout << "2000 random inputs parsed without crashing\n";
}
'''))
