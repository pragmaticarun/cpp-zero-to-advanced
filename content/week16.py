WEEK = dict(num=16, title="C++ in the real world: interop, embedded, design, and what's next", intro="""
The final week zooms out. C++ rarely lives alone: it talks to C, Python, Java/Android and hardware. We look
at embedded constraints, the design patterns and API design principles that make large C++ codebases
maintainable, and finish with a tour of C++26. Then it's capstone time.
""", lessons=[
dict(title="Interoperability: C, Python (pybind11), and Java/Android (JNI)", std="C++20", minutes=13, area="Interop",
features=[("Designing a C ABI wrapper around C++ (opaque handles)", "—"), ("Exceptions must not cross C boundaries", "C++11"), ("Callbacks with `void*` user data", "—"), ("pybind11 / nanobind bindings", "—"), ("JNI and the Android NDK", "—"), ("Ownership across language boundaries", "—")],
why="""
Your C++ DSP engine is great — now the Python data team, the Android app and a legacy C codebase all want
it. The universal adapter is a **C API**: every language can call C. On top of it (or directly), tools like
pybind11 and JNI make C++ feel native in Python and Java.
""",
body="""
## The opaque-handle pattern

Expose a C API with an incomplete type and create/destroy functions; never let C++ exceptions or types
cross the boundary:

{{ex}}

Rules: catch everything at the boundary (`try { ... } catch (...) { return error_code; }`) — an exception
unwinding into C is undefined behaviour. Pass callbacks as a function pointer plus `void* user_data`.
Document who frees what.

## Python with pybind11

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;
PYBIND11_MODULE(dsp, m) {
    py::class_<Gain>(m, "Gain")
        .def(py::init<double>())
        .def("apply", &Gain::apply)
        .def_property_readonly("db", &Gain::db);
    m.def("rms", &rms, "Root mean square of a list of samples");
}
```

Build with CMake + `pybind11_add_module`, then `import dsp` in Python. pybind11 converts STL types and
translates exceptions to Python exceptions. **nanobind** is a lighter, faster successor. Release the GIL
(`py::gil_scoped_release`) around long C++ computations.

## Java/Android with JNI

```cpp
extern "C" JNIEXPORT jdouble JNICALL
Java_com_example_dsp_Native_rms(JNIEnv* env, jclass, jfloatArray samples) {
    jsize n = env->GetArrayLength(samples);
    jfloat* p = env->GetFloatArrayElements(samples, nullptr);
    double r = rms({p, static_cast<std::size_t>(n)});
    env->ReleaseFloatArrayElements(samples, p, JNI_ABORT);   // always release!
    return r;
}
```

On Android, the NDK builds C++ with CMake (`externalNativeBuild`) and you load it with
`System.loadLibrary("dsp")`. JNI local references, array pinning and thread attachment
(`AttachCurrentThread`) are the common traps.
""",
files={"": r'''
#include <cmath>
#include <cstdio>
#include <iostream>
#include <new>
#include <stdexcept>
#include <string>
#include <vector>

// ===== dsp.h — what C (and every FFI) sees =====
extern "C" {
typedef struct dsp_mixer dsp_mixer;                       // opaque handle
typedef void (*dsp_level_cb)(double level, void* user);
enum { DSP_OK = 0, DSP_ERR_ARG = 1, DSP_ERR_INTERNAL = 2 };
dsp_mixer* dsp_mixer_create(int channels);
void dsp_mixer_destroy(dsp_mixer* m);
int dsp_mixer_process(dsp_mixer* m, const float* samples, int n, dsp_level_cb cb, void* user);
}

// ===== dsp.cpp — the C++ implementation =====
struct dsp_mixer {
    int channels;
    std::vector<float> scratch;
    double process(const float* s, int n) {
        if (n < 0) throw std::invalid_argument{"negative length"};
        scratch.assign(s, s + n);
        double sum = 0; for (float x : scratch) sum += static_cast<double>(x) * x;
        return n ? std::sqrt(sum / n) : 0.0;
    }
};

extern "C" dsp_mixer* dsp_mixer_create(int channels) {
    try { return new dsp_mixer{channels, {}}; } catch (...) { return nullptr; }
}
extern "C" void dsp_mixer_destroy(dsp_mixer* m) { delete m; }
extern "C" int dsp_mixer_process(dsp_mixer* m, const float* s, int n, dsp_level_cb cb, void* user) {
    if (!m || (!s && n > 0)) return DSP_ERR_ARG;
    try {                                                 // no exception may escape into C
        double level = m->process(s, n);
        if (cb) cb(level, user);
        return DSP_OK;
    } catch (const std::invalid_argument&) { return DSP_ERR_ARG; }
    catch (...) { return DSP_ERR_INTERNAL; }
}

// ===== a "C client" =====
static void on_level(double level, void* user) {
    *static_cast<double*>(user) = level;
}

int main() {
    dsp_mixer* m = dsp_mixer_create(2);
    float samples[] = {0.5f, -0.5f, 0.5f, -0.5f};
    double level = 0;
    int rc = dsp_mixer_process(m, samples, 4, on_level, &level);
    std::printf("rc=%d level=%.3f\n", rc, level);
    rc = dsp_mixer_process(m, samples, -1, on_level, &level);
    std::printf("negative length -> rc=%d (exception stayed inside C++)\n", rc);
    std::printf("null handle -> rc=%d\n", dsp_mixer_process(nullptr, samples, 4, nullptr, nullptr));
    dsp_mixer_destroy(m);
}
'''},
takeaways=["A C API with opaque handles is the universal interop layer.",
"Never let exceptions cross a C boundary; convert them to error codes.",
"pybind11/nanobind bind C++ to Python; JNI/NDK bind it to Java/Android.",
"Make ownership explicit across language boundaries."],
quiz=[("Why must `dsp_mixer_process` catch all exceptions?", "Unwinding through C frames (or into another language's runtime) is undefined behaviour."),
("How does a C callback get access to the caller's state?", "Through a `void* user_data` parameter passed back to the callback."),
("What does `JNI_ABORT` in `ReleaseFloatArrayElements` mean?", "Free the buffer without copying changes back to the Java array (we only read it).")]),

dict(title="Embedded and real-time C++", std="C++20", minutes=13, area="Embedded",
features=[("Freestanding implementations; `-fno-exceptions`, `-fno-rtti`", "—"), ("Memory-mapped registers with `volatile`", "C++98"), ("No dynamic allocation after init; static pools", "—"), ("Fixed-point arithmetic", "—"), ("`constexpr` lookup tables", "C++11/20"), ("Interrupt-safe data sharing (atomics, critical sections)", "C++11"), ("`std::bit_cast`, `<bit>` operations", "C++20"), ("Deprecated compound `volatile` operations", "C++20")],
why="""
A microcontroller might have 64 KB of flash, 16 KB of RAM, no OS, and an interrupt that must be serviced in
2 µs. C++ is excellent here — templates and `constexpr` cost nothing at run time — but you have to choose the
right subset: no heap after startup, often no exceptions or RTTI, and very deliberate access to hardware.
""",
body="""
## The embedded subset

- **No heap after init**: fragmentation and non-deterministic timing. Use static storage, fixed-capacity
  containers (`std::array`, the ring buffer capstone, C++26 `std::inplace_vector`), and pools.
- **Exceptions/RTTI** are often disabled (`-fno-exceptions -fno-rtti`) for code size and determinism; use
  error codes / `std::expected`.
- **Compute at compile time**: `constexpr` tables live in flash, not RAM.

## Hardware registers

```cpp
struct Uart { volatile std::uint32_t data, status, ctrl; };
inline Uart& uart0 = *reinterpret_cast<Uart*>(0x4000'1000);   // on real hardware
```

`volatile` tells the compiler every access matters (it can't cache or remove them). C++20 deprecated
compound operations like `reg |= bit` on volatile because they suggest atomicity that doesn't exist; write
`reg = reg | bit`. Below we simulate a register block in RAM so the example runs anywhere.

{{ex}}

## Fixed-point

Many MCUs lack an FPU. Q15 fixed-point stores values in [-1, 1) as `int16_t` scaled by 2^15; multiplication
is `(a * b) >> 15` in 32-bit. The example implements a Q15 gain with saturation.

## Sharing with interrupts

An ISR and the main loop share data like threads do. Use `std::atomic` (if lock-free on the target) or a
critical section (disable interrupts briefly). The SPSC ring buffer from Week 14 is the classic ISR→main
channel — see Capstone B.
""",
files={"": r'''
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>

// ---- simulated memory-mapped peripheral ----
struct GpioRegs {
    volatile std::uint32_t mode;
    volatile std::uint32_t out;
    volatile std::uint32_t in;
};
GpioRegs fake_gpio{};                                    // on hardware: *reinterpret_cast<GpioRegs*>(0x48000000)

constexpr std::uint32_t pin(unsigned n) { return 1u << n; }
void led_on(GpioRegs& g, unsigned n) { g.out = g.out | pin(n); }      // not `|=`: deprecated on volatile
void led_off(GpioRegs& g, unsigned n) { g.out = g.out & ~pin(n); }

// ---- Q15 fixed point ----
using q15 = std::int16_t;
constexpr q15 to_q15(double x) { return static_cast<q15>(x * 32768.0 >= 32767.0 ? 32767 : x * 32768.0); }
constexpr q15 q15_mul(q15 a, q15 b) {
    std::int32_t p = (static_cast<std::int32_t>(a) * b) >> 15;
    return static_cast<q15>(p > 32767 ? 32767 : (p < -32768 ? -32768 : p));
}

// ---- compile-time lookup table (lives in flash on an MCU) ----
constexpr auto make_square_table() {
    std::array<std::uint16_t, 16> t{};
    for (std::size_t i = 0; i < t.size(); ++i) t[i] = static_cast<std::uint16_t>(i * i);
    return t;
}
constexpr auto kSquares = make_square_table();
static_assert(kSquares[15] == 225);

// ---- a static pool: fixed number of objects, no heap ----
template <typename T, std::size_t N>
class StaticPool {
public:
    T* acquire() { for (std::size_t i = 0; i < N; ++i) if (!used_[i]) { used_[i] = true; return &items_[i]; } return nullptr; }
    void release(T* p) { used_[static_cast<std::size_t>(p - items_.data())] = false; }
private:
    std::array<T, N> items_{};
    std::array<bool, N> used_{};
};

int main() {
    led_on(fake_gpio, 5);
    led_on(fake_gpio, 0);
    led_off(fake_gpio, 5);
    std::cout << "GPIO out = 0x" << std::hex << fake_gpio.out << std::dec << '\n';

    q15 half = to_q15(0.5), gain = to_q15(0.25);
    std::cout << "0.5 * 0.25 in Q15 = " << q15_mul(half, gain) << " (" << q15_mul(half, gain) / 32768.0 << ")\n";
    std::cout << "saturating -1 * -1 = " << q15_mul(-32768, -32768) << '\n';

    std::cout << "kSquares[12] = " << kSquares[12] << '\n';
    std::cout << "popcount(0xF0F0) = " << std::popcount(0xF0F0u) << ", bit_width(1000) = " << std::bit_width(1000u)
              << ", float bits = 0x" << std::hex << std::bit_cast<std::uint32_t>(1.0f) << std::dec << '\n';

    StaticPool<int, 2> pool;
    int* a = pool.acquire(); int* b = pool.acquire(); int* c = pool.acquire();
    std::cout << "pool: a " << (a ? "ok" : "null") << ", b " << (b ? "ok" : "null") << ", c " << (c ? "ok" : "null") << '\n';
    pool.release(a);
    std::cout << "after release: " << (pool.acquire() ? "ok" : "null") << '\n';
}
'''},
takeaways=["Embedded C++ avoids the heap after init and often disables exceptions/RTTI.",
"`volatile` is for hardware registers; avoid compound ops on volatile (deprecated in C++20).",
"`constexpr` tables, fixed-point math and static pools give deterministic, small code.",
"Share data with ISRs via lock-free atomics or brief critical sections (SPSC ring buffer)."],
quiz=[("Why avoid dynamic allocation after startup on an MCU?", "Fragmentation and non-deterministic timing can cause failures or missed deadlines."),
("Why did C++20 deprecate `reg |= bit` on a volatile?", "It looks atomic but is a separate read and write; writing it out makes the two accesses explicit."),
("What is 0.5 × 0.25 in Q15 as an integer?", "4096 (0.125 × 32768).")]),

dict(title="Design patterns in modern C++", std="C++20", minutes=13, area="Design",
features=[("Strategy via `std::function`, templates, or concepts", "C++11/20"), ("Observer with lifetime safety (`weak_ptr` / tokens)", "C++11"), ("Factory and registry", "—"), ("Visitor via `std::variant` + `std::visit`", "C++17"), ("Pimpl idiom (recap) and type erasure (recap)", "C++11"), ("RAII scope guards", "C++11"), ("Policy-based design", "C++98")],
why="""
Classic design patterns were described for 1990s Java and C++. Modern C++ often expresses them more simply:
a strategy can be a lambda, a visitor can be `std::visit` over a variant, and an observer must care about
*lifetimes* (who unsubscribes when an object dies?). Knowing the modern form keeps designs small.
""",
body="""
## Modern forms of classic patterns

| Pattern | Classic | Modern C++ |
|---|---|---|
| Strategy | interface + subclasses | `std::function`, template parameter, or concept |
| Visitor | double dispatch with `accept` | `std::variant` + `std::visit` (closed set of types) |
| Observer | raw listener pointers | subscription tokens / `weak_ptr` to avoid dangling |
| Factory | `switch` on type name | registry map of creator functions |
| Template method | virtual hooks | NVI (Week 6) or CRTP (Week 8) |
| Scope guard | try/finally | RAII object with a lambda |

{{ex}}

The observer uses `weak_ptr` so a destroyed listener is skipped automatically — no dangling callbacks.

## When *not* to use a pattern

Patterns are vocabulary, not goals. If a plain function solves it, write a plain function. Every
indirection (virtual call, `std::function`, registry) costs readability; add it when you need the
flexibility, not before.
""",
files={"": r'''
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <type_traits>
#include <variant>
#include <vector>

// Strategy: just a callable
using Interp = std::function<double(double, double, double)>;
double sample(double a, double b, double t, const Interp& how) { return how(a, b, t); }

// Visitor over a closed set of shapes
struct Circle { double r; };
struct Rect { double w, h; };
using Shape = std::variant<Circle, Rect>;
template <typename... Fs> struct overloaded : Fs... { using Fs::operator()...; };

// Observer with weak_ptr: dead listeners are skipped and pruned
class Meter {
public:
    using Listener = std::function<void(double)>;
    void subscribe(const std::shared_ptr<Listener>& l) { listeners_.push_back(l); }
    void publish(double v) {
        std::erase_if(listeners_, [](const auto& w) { return w.expired(); });
        for (auto& w : listeners_) if (auto l = w.lock()) (*l)(v);
    }
    std::size_t count() const { return listeners_.size(); }
private:
    std::vector<std::weak_ptr<Listener>> listeners_;
};

// Factory registry
struct Effect { virtual ~Effect() = default; virtual std::string name() const = 0; };
struct Reverb : Effect { std::string name() const override { return "reverb"; } };
struct Delay : Effect { std::string name() const override { return "delay"; } };
std::map<std::string, std::function<std::unique_ptr<Effect>()>>& registry() {
    static std::map<std::string, std::function<std::unique_ptr<Effect>()>> r{
        {"reverb", [] { return std::make_unique<Reverb>(); }},
        {"delay", [] { return std::make_unique<Delay>(); }}};
    return r;
}

// Scope guard
template <typename F> struct ScopeExit { F f; ~ScopeExit() { f(); } };
template <typename F> ScopeExit(F) -> ScopeExit<F>;

int main() {
    std::cout << "linear " << sample(0, 10, 0.3, [](double a, double b, double t) { return a + (b - a) * t; })
              << ", step " << sample(0, 10, 0.3, [](double a, double b, double t) { return t < 0.5 ? a : b; }) << '\n';

    std::vector<Shape> shapes{Circle{1.0}, Rect{2, 3}};
    for (const auto& s : shapes)
        std::visit(overloaded{[](const Circle& c) { std::cout << "circle area " << 3.14159 * c.r * c.r << '\n'; },
                              [](const Rect& r) { std::cout << "rect area " << r.w * r.h << '\n'; }}, s);

    Meter meter;
    auto keep = std::make_shared<Meter::Listener>([](double v) { std::cout << "ui got " << v << '\n'; });
    meter.subscribe(keep);
    {
        auto temp = std::make_shared<Meter::Listener>([](double v) { std::cout << "logger got " << v << '\n'; });
        meter.subscribe(temp);
        meter.publish(-6.0);
    }                                               // logger destroyed
    meter.publish(-3.0);
    std::cout << "listeners now " << meter.count() << '\n';

    for (const char* n : {"delay", "reverb", "chorus"}) {
        auto it = registry().find(n);
        std::cout << n << " -> " << (it != registry().end() ? it->second()->name() : std::string{"unknown effect"}) << '\n';
    }

    {
        ScopeExit guard{[] { std::cout << "scope guard ran\n"; }};
        std::cout << "doing work\n";
    }
}
'''},
takeaways=["Many patterns shrink in modern C++: strategy = callable, visitor = `std::visit`.",
"Observers must handle listener lifetime; `weak_ptr` or tokens avoid dangling callbacks.",
"Registries of creator functions make extensible factories.",
"Use a pattern when you need its flexibility, not by default."],
quiz=[("When is `std::variant` + `std::visit` better than a virtual-function hierarchy?", "When the set of types is closed and known, and you want to add operations easily without touching the types."),
("What bug does `weak_ptr` prevent in the observer?", "Calling a listener that has been destroyed (dangling callback)."),
("What's the cost of using `std::function` for a strategy?", "Type erasure: possible heap allocation and an indirect call that's hard to inline; a template parameter avoids it.")]),

dict(title="API and library design", std="C++23", minutes=12, area="Design",
features=[("Strong types to prevent argument mix-ups", "C++11"), ("`[[nodiscard]]` (with reason), `[[deprecated]]`", "C++17/20"), ("Choosing an error-handling policy for a library", "—"), ("Const-correctness and value semantics in interfaces", "C++98"), ("Inline namespaces for API versioning", "C++11"), ("Header hygiene and minimal includes", "—"), ("Semantic versioning and ABI policy", "—")],
why="""
`set_volume(0.8, 1)` — is that 80% on channel 1, or volume 1 with 0.8 seconds fade? Good APIs make
correct use easy and incorrect use hard *at compile time*. A library's interface outlives its
implementation by years; this lesson is about getting it right.
""",
body="""
## Principles

1. **Make illegal states unrepresentable**: strong types (`Gain`, `Channel`, `Milliseconds`) instead of
   naked `double`/`int`; enums instead of `bool` flags.
2. **Mark results that must be used**: `[[nodiscard("check the error")]]`.
3. **Pick one error policy** per library (Week 9) and document it.
4. **Value semantics and const-correctness**: take `const T&`/`std::string_view`/`std::span` for inputs,
   return values, avoid out-parameters.
5. **Evolve without breaking**: `[[deprecated("use X")]]`, inline namespaces for versioning, keep ABI
   policies explicit (pimpl, Week 15).

{{ex}}

## Checklist for a public header

- Includes only what it needs (consider forward declarations).
- No `using namespace` at header scope.
- Everything in a project namespace.
- Every function documents preconditions, errors, and ownership.
- Tests use only the public API.
""",
files={"": r'''
#include <chrono>
#include <expected>
#include <iostream>
#include <string>
#include <string_view>

namespace mixer {
inline namespace v2 {                                   // default version; v1 kept for old clients

struct Channel { int index; explicit constexpr Channel(int i) : index{i} {} };
struct Gain {
    double linear;
    static constexpr Gain from_percent(double p) { return Gain{p / 100.0}; }
};
using Fade = std::chrono::milliseconds;

enum class Error { bad_channel, out_of_range };
constexpr std::string_view describe(Error e) { return e == Error::bad_channel ? "bad channel" : "gain out of range"; }

class Console {
public:
    [[nodiscard("check whether the change was applied")]]
    std::expected<void, Error> set_volume(Channel ch, Gain g, Fade fade = Fade{0}) {
        if (ch.index < 0 || ch.index >= 8) return std::unexpected{Error::bad_channel};
        if (g.linear < 0 || g.linear > 2) return std::unexpected{Error::out_of_range};
        std::cout << "ch" << ch.index << " -> " << g.linear << " over " << fade.count() << "ms\n";
        return {};
    }
    [[deprecated("use set_volume(Channel, Gain, Fade)")]]
    bool setVol(int ch, double v) { return set_volume(Channel{ch}, Gain{v}).has_value(); }
};

}  // namespace v2
namespace v1 { inline int api_version() { return 1; } }
inline int api_version() { return 2; }
}  // namespace mixer

int main() {
    using namespace std::chrono_literals;
    mixer::Console c;
    // c.set_volume(0.8, 1);                            // won't compile: arguments can't be mixed up
    if (auto r = c.set_volume(mixer::Channel{1}, mixer::Gain::from_percent(80), 250ms); !r)
        std::cout << "error: " << describe(r.error()) << '\n';
    if (auto r = c.set_volume(mixer::Channel{9}, mixer::Gain{0.5}); !r)
        std::cout << "error: " << describe(r.error()) << '\n';
    std::cout << "api v" << mixer::api_version() << " (old clients can call v1: " << mixer::v1::api_version() << ")\n";
}
''', "std": "c++23"},
takeaways=["Strong types and enums turn argument mix-ups into compile errors.",
"`[[nodiscard]]` and `std::expected` make errors hard to ignore.",
"Use `[[deprecated]]` and inline namespaces to evolve APIs without breaking users.",
"Keep public headers minimal, namespaced and fully documented."],
quiz=[("Why is `void f(bool fast, bool safe)` a weak signature?", "Call sites like `f(true, false)` are unreadable and easy to swap; use enums or strong types."),
("What does an inline namespace give you for versioning?", "Its contents are accessible from the enclosing namespace by default, while older versions remain addressable explicitly (and mangled names differ per version)."),
("What happens when a caller ignores a `[[nodiscard]]` result?", "The compiler warns (an error with `-Werror`).")]),

dict(title="C++26 preview: reflection, contracts, std::execution, and more", std="C++26", minutes=14, area="C++26 preview",
features=[("Static reflection (`^^T`, `std::meta`, splicers)", "C++26 (preview)"), ("Contracts: `pre`, `post`, `contract_assert`", "C++26 (preview)"), ("`std::execution` senders/receivers", "C++26 (preview)"), ("`std::inplace_vector`", "C++26 (preview)"), ("Pack indexing `Ts...[N]`", "C++26 (preview)"), ("`= delete(\"reason\")`", "C++26 (preview)"), ("Placeholder variables `_`", "C++26 (preview)"), ("`#embed`", "C++26 (preview)"), ("`std::simd`, `std::hazard_pointer`, `std::rcu`", "C++26 (preview)"), ("Erroneous behaviour; hardened standard library", "C++26 (preview)")],
why="""
C++26 is the biggest release since C++11. Static reflection alone will change how we write serialization,
bindings and logging. Compilers are implementing it now, so this lesson is honest about status: the C++26
code below is **not compiled by our checker** (marked preview); the runnable example shows the C++23 code
you write *today* for the same problems, so you can see what C++26 will replace.
""",
body="""
## Static reflection (P2996)

```cpp
// C++26 (preview): print any aggregate's fields with no macros
template <typename T>
void print_fields(const T& obj) {
    template for (constexpr auto m : std::define_static_array(std::meta::nonstatic_data_members_of(^^T, std::meta::access_context::current())))
        std::println("{} = {}", std::meta::identifier_of(m), obj.[:m:]);
}
```

`^^T` reflects a type into a `std::meta::info` value; `[: m :]` splices it back into code. Serialization,
enum-to-string, ORM mappings and Python bindings become library code instead of macros or code generators.
(Experimental implementations: Bloomberg's clang-p2996 fork and EDG; GCC 16 has initial support.)

## Contracts (P2900)

```cpp
double rms(std::span<const float> xs)
    pre(!xs.empty())
    post(r: r >= 0.0);
```

Preconditions and postconditions become part of the declaration, checked according to a build-selected
evaluation semantic (ignore, observe, enforce, quick-enforce). `contract_assert(expr)` replaces `assert`.

## `std::execution` (P2300)

```cpp
auto work = stdexec::schedule(pool.get_scheduler())
          | stdexec::then([] { return decode(); })
          | stdexec::then([](Audio a) { return analyze(a); });
auto [report] = stdexec::sync_wait(std::move(work)).value();
```

Composable, cancellable async work with explicit schedulers — usable today via NVIDIA's `stdexec`.

## Smaller but welcome

- `std::inplace_vector<T, N>`: a vector with fixed capacity and no heap — perfect for embedded (Week 16.2).
- Pack indexing: `Ts...[0]` is the first type in a pack.
- `void f(int) = delete("use f(Channel)");` — deletion with a reason.
- `auto [_, value] = pair;` — `_` placeholders you can reuse.
- `#embed "logo.png"` — include binary data at compile time.
- `std::simd`, `std::hazard_pointer`, `std::rcu`, `std::linalg`, saturating arithmetic (`std::add_sat`).
- **Erroneous behaviour**: reading an uninitialized variable is no longer UB but "erroneous" (a defined,
  diagnosable value); hardened library preconditions are standardized.

## What you write today

{{ex}}

Each block is the C++23 workaround for a C++26 feature: manual field lists (→ reflection), an assert macro
(→ contracts), `std::array` + size (→ `inplace_vector`), `std::tuple_element` (→ pack indexing),
`std::add_sat` emulation (→ saturating arithmetic).
""",
files={"": r'''
#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <span>
#include <stdexcept>
#include <string_view>
#include <tuple>
#include <type_traits>

// (1) Reflection today: list fields by hand (C++26: std::meta::nonstatic_data_members_of)
struct Settings { int rate; int bits; double gain; };
template <typename F> void for_each_field(const Settings& s, F f) { f("rate", s.rate); f("bits", s.bits); f("gain", s.gain); }

// (2) Contracts today: a macro (C++26: pre(...) / post(...) / contract_assert)
#define EXPECTS(cond) ((cond) ? void(0) : throw std::logic_error{"precondition failed: " #cond})
double mean(std::span<const double> xs) {
    EXPECTS(!xs.empty());
    double s = 0; for (double x : xs) s += x;
    return s / static_cast<double>(xs.size());
}

// (3) inplace_vector today: array + size (C++26: std::inplace_vector<T, N>)
template <typename T, std::size_t N>
struct FixedVec {
    std::array<T, N> data{}; std::size_t n = 0;
    bool push_back(const T& v) { if (n == N) return false; data[n++] = v; return true; }
    std::size_t size() const { return n; }
};

// (4) Pack indexing today (C++26: Ts...[0])
template <typename... Ts> using first_t = std::tuple_element_t<0, std::tuple<Ts...>>;
static_assert(std::is_same_v<first_t<int, double>, int>);

// (5) Saturating add today (C++26: std::add_sat)
constexpr std::int16_t add_sat16(std::int16_t a, std::int16_t b) {
    int r = a + b;
    return static_cast<std::int16_t>(r > std::numeric_limits<std::int16_t>::max() ? std::numeric_limits<std::int16_t>::max()
                                   : r < std::numeric_limits<std::int16_t>::min() ? std::numeric_limits<std::int16_t>::min() : r);
}

int main() {
    for_each_field(Settings{48000, 24, 0.5}, [](std::string_view name, auto v) { std::cout << name << " = " << v << '\n'; });
    double xs[] = {1, 2, 3};
    std::cout << "mean " << mean(xs) << '\n';
    try { (void)mean({}); } catch (const std::logic_error& e) { std::cout << e.what() << '\n'; }
    FixedVec<int, 2> fv;
    std::cout << std::boolalpha << fv.push_back(1) << ' ' << fv.push_back(2) << ' ' << fv.push_back(3) << " size " << fv.size() << '\n';
    std::cout << "add_sat16(30000, 10000) = " << add_sat16(30000, 10000) << '\n';
}
''', "std": "c++23"},
takeaways=["Static reflection (C++26) turns macros and code generators into ordinary library code.",
"Contracts make preconditions/postconditions part of declarations with selectable checking.",
"`std::execution` provides composable, cancellable async work; usable today via stdexec.",
"Many smaller features (inplace_vector, pack indexing, `_`, `#embed`, saturating math) remove workarounds."],
quiz=[("What does `^^T` produce in C++26?", "A `std::meta::info` value representing the type `T` at compile time."),
("How do C++26 contracts differ from `assert`?", "They're part of the function declaration (visible to callers and tools) and have standardized evaluation semantics selectable at build time."),
("Which C++26 container replaces a hand-written fixed-capacity vector?", "`std::inplace_vector<T, N>`.")]),
],
assignment=dict(title="Ship a library", task="""
Package one of your earlier assignments (e.g. the LRU cache or the config parser) as a library: a namespaced
public header with strong types and `[[nodiscard]]`, a C API wrapper with opaque handles and error codes,
tests, and a CMakeLists.txt with PUBLIC/PRIVATE usage requirements. The reference solution shows the C API
wrapper over the LRU cache, exercised from "C-style" client code.
""", std="c++20", solution=r'''
#include <cstdio>
#include <cstring>
#include <list>
#include <string>
#include <unordered_map>
#include <utility>

namespace cache {
class Lru {
public:
    explicit Lru(std::size_t cap) : cap_{cap} {}
    [[nodiscard]] const std::string* get(const std::string& k) {
        auto it = index_.find(k);
        if (it == index_.end()) return nullptr;
        order_.splice(order_.begin(), order_, it->second);
        return &it->second->second;
    }
    void put(std::string k, std::string v) {
        if (auto it = index_.find(k); it != index_.end()) { it->second->second = std::move(v); order_.splice(order_.begin(), order_, it->second); return; }
        if (order_.size() == cap_) { index_.erase(order_.back().first); order_.pop_back(); }
        order_.emplace_front(k, std::move(v));
        index_[std::move(k)] = order_.begin();
    }
    std::size_t size() const { return order_.size(); }
private:
    std::size_t cap_;
    std::list<std::pair<std::string, std::string>> order_;
    std::unordered_map<std::string, std::list<std::pair<std::string, std::string>>::iterator> index_;
};
}  // namespace cache

extern "C" {
typedef struct lru_cache lru_cache;
enum { LRU_OK = 0, LRU_MISS = 1, LRU_ERR = 2, LRU_TOO_SMALL = 3 };
lru_cache* lru_create(size_t capacity);
void lru_destroy(lru_cache* c);
int lru_put(lru_cache* c, const char* key, const char* value);
int lru_get(lru_cache* c, const char* key, char* out, size_t out_size);
}

struct lru_cache { cache::Lru impl; };

extern "C" lru_cache* lru_create(size_t capacity) {
    if (capacity == 0) return nullptr;
    try { return new lru_cache{cache::Lru{capacity}}; } catch (...) { return nullptr; }
}
extern "C" void lru_destroy(lru_cache* c) { delete c; }
extern "C" int lru_put(lru_cache* c, const char* key, const char* value) {
    if (!c || !key || !value) return LRU_ERR;
    try { c->impl.put(key, value); return LRU_OK; } catch (...) { return LRU_ERR; }
}
extern "C" int lru_get(lru_cache* c, const char* key, char* out, size_t out_size) {
    if (!c || !key || !out || out_size == 0) return LRU_ERR;
    try {
        const std::string* v = c->impl.get(key);
        if (!v) return LRU_MISS;
        if (v->size() + 1 > out_size) return LRU_TOO_SMALL;
        std::memcpy(out, v->c_str(), v->size() + 1);
        return LRU_OK;
    } catch (...) { return LRU_ERR; }
}

int main() {                                           // written like C client code
    lru_cache* c = lru_create(2);
    lru_put(c, "kick", "kick.wav");
    lru_put(c, "snare", "snare.wav");
    char buf[32];
    if (lru_get(c, "kick", buf, sizeof buf) == LRU_OK) std::printf("kick -> %s\n", buf);
    lru_put(c, "hat", "hat.wav");                       // evicts snare (least recently used)
    std::printf("snare -> %s\n", lru_get(c, "snare", buf, sizeof buf) == LRU_MISS ? "(evicted)" : buf);
    char tiny[4];
    std::printf("small buffer -> rc=%d\n", lru_get(c, "hat", tiny, sizeof tiny));
    std::printf("create(0) -> %s\n", lru_create(0) ? "handle" : "NULL");
    lru_destroy(c);
}
'''))
