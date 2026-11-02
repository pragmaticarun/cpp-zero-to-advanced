WEEK = dict(num=3, title="Memory: arrays, pointers, strings, bits", intro="""
This is the week where C++ shows its systems-language roots. We'll look at how objects sit in memory,
how pointers work, what goes wrong with manual memory management (and why modern C++ rarely does it), how
text is stored, and how to manipulate individual bits.

It's also the week where we meet **undefined behaviour** properly. Don't worry — the goal isn't to scare
you, it's to give you a clear map of where the cliffs are, so you can walk confidently everywhere else.
""", lessons=[
dict(title="Arrays: C arrays, std::array, and a first look at std::span", std="C++20", minutes=10, area="Basics: memory",
features=[("Built-in (C) arrays and array-to-pointer decay", "C++98"), ("`std::array`", "C++11"), ("`std::size`, `std::ssize`, `std::data`", "C++20"), ("`std::span` (non-owning view)", "C++20"), ("Out-of-bounds access is UB; `.at()` bounds-checked", "C++98")],
why="""
Audio and video code is full of fixed-size buffers: a 1024-sample FFT window, a 16-entry lookup table,
a 4×4 matrix. Arrays are the simplest container there is — but C-style arrays have a nasty habit of
forgetting their own size the moment you pass them to a function. Let's see the problem and the modern fixes.
""",
body="""
## C arrays, and how they forget their size

```cpp
int window[4] = {1, 2, 3, 4};
std::cout << sizeof(window);     // 16: the whole array (4 * sizeof(int))

void f(int a[4]) {               // looks like an array parameter...
    std::cout << sizeof(a);      // 8: it's really `int* a`!
}
```

When you pass a C array to a function, it **decays** to a pointer to its first element. The size is gone
— the `[4]` in the parameter is ignored. This is where countless buffer overflows begin.

## `std::array`: an array that behaves like a value

`std::array<int, 4>` is a thin wrapper around a C array with zero overhead. It knows its size, can be
copied and compared, and can be returned from functions.

## `std::span`: "a view of some contiguous elements" (C++20)

When a function just needs to *look at* a sequence of elements, take a `std::span<const T>`. A span is a
pointer plus a length; it doesn't own anything. It accepts C arrays, `std::array`, and `std::vector`
alike — and it can't forget its size.

{{ex}}

## Bounds

`a[i]` with `i` out of range is **undefined behaviour** — no exception, no guaranteed crash. `std::array`
and `std::vector` offer `.at(i)` which throws `std::out_of_range`. In debug builds you can also turn on
library assertions (`-D_GLIBCXX_ASSERTIONS` for libstdc++, hardening modes in libc++) to catch bad
`operator[]` indexes; many distributions enable that by default now.

!!! tip "Pro tip"
    Rule of thumb: **own** data with `std::array` / `std::vector`; **pass** it to functions as
    `std::span<const T>` (read) or `std::span<T>` (write). We'll revisit spans and `mdspan` in Week 10.
""",
files={"": r'''
#include <array>
#include <iostream>
#include <numeric>
#include <span>
#include <vector>

// One function works for C arrays, std::array and std::vector.
double mean(std::span<const float> xs) {
    if (xs.empty()) return 0.0;
    return std::accumulate(xs.begin(), xs.end(), 0.0) / static_cast<double>(xs.size());
}

void apply_gain(std::span<float> xs, float g) {
    for (auto& x : xs) x *= g;
}

int main() {
    float c_array[4] = {1, 2, 3, 4};
    std::array<float, 4> arr{1, 2, 3, 4};
    std::vector<float> vec{1, 2, 3, 4, 5, 6};

    std::cout << "sizeof(c_array)=" << sizeof(c_array) << " std::size(c_array)=" << std::size(c_array) << '\n';
    std::cout << mean(c_array) << ' ' << mean(arr) << ' ' << mean(vec) << '\n';

    apply_gain(std::span(vec).subspan(2, 2), 10.0f);   // only elements 2 and 3
    for (float x : vec) std::cout << x << ' ';
    std::cout << '\n';

    std::array<float, 4> copy = arr;   // std::array copies like a value
    std::cout << std::boolalpha << (copy == arr) << '\n';
    try {
        std::cout << arr.at(10) << '\n';
    } catch (const std::out_of_range&) {
        std::cout << "at(10) threw out_of_range\n";
    }
}
'''},
takeaways=["C arrays decay to pointers when passed to functions and lose their size.",
"`std::array<T, N>` is a zero-overhead fixed array with value semantics.",
"Pass contiguous data as `std::span<const T>` / `std::span<T>` — one signature for all containers.",
"Out-of-bounds `[]` is UB; `.at()` throws; library hardening catches it in debug builds."],
quiz=[("Inside `void f(int a[10])`, what is `sizeof(a)` on a 64-bit system?", "8 — the parameter is actually `int*`; the 10 is ignored."),
("Does `std::span` own its elements?", "No. It is a non-owning view (pointer + size). The underlying storage must outlive the span."),
("What's the difference between `arr[10]` and `arr.at(10)` for a `std::array<int, 4>`?", "`arr[10]` is undefined behaviour; `arr.at(10)` throws `std::out_of_range`.")]),

dict(title="Pointers: addresses, arithmetic, and const", std="C++20", minutes=12, area="Basics: memory",
features=[("Pointers, `&` address-of, `*` dereference, `->`", "C++98"), ("`nullptr` checks", "C++11"), ("Pointer arithmetic within an array", "C++98"), ("`const T*` vs `T* const`", "C++98"), ("Pointers vs references: when to use which", "—"), ("`void*` and why to avoid it", "C++98")],
why="""
Pointers have a scary reputation, but the idea is simple: a pointer is a variable that holds the *address*
of another object. Android's NDK APIs, every C library, and hardware registers all speak in pointers, so
you need to be fluent. Let's build the picture step by step.
""",
body="""
## The idea

```cpp
int level = 42;
int* p = &level;   // p holds the address of level
*p = 7;            // dereference: "the object p points to" -> level is now 7
```

Draw it as a box (`level`, containing 42) and an arrow (`p`) pointing at it. Unlike a reference, a
pointer can be *null* (point at nothing) and can be *re-pointed* to another object.

| | Reference `T&` | Pointer `T*` |
|---|---|---|
| can be null | no | yes (`nullptr`) |
| can be re-seated | no | yes |
| syntax to use | like the object | `*p`, `p->member` |
| use when | always refers to something | "optional" object, or re-pointing, or C APIs |

## Pointer arithmetic

If `p` points into an array, `p + 1` points to the *next element* (not the next byte). `p[i]` is exactly
`*(p + i)`. Arithmetic is only valid *within* the same array (and one-past-the-end); going outside is UB.

## const and pointers: read right to left

```cpp
const int* a;        // pointer to const int: can't modify *a, can re-point a
int* const b = &x;   // const pointer to int: can modify *b, can't re-point b
const int* const c = &x;  // neither
```

Trick: read the declaration right-to-left. `int* const b` = "b is a const pointer to int".

{{ex}}

## The wrong way: dereferencing null or dangling pointers

```cpp
int* p = nullptr;
*p = 1;              // UB: often a crash (SIGSEGV), but not guaranteed

int* q;
{ int local = 5; q = &local; }
*q = 6;              // UB: local is dead, q dangles
```

The fix is mostly *design*: prefer references when null isn't meaningful, keep pointers non-owning
(owning pointers are smart pointers — Week 12), and don't let a pointer outlive what it points to.

!!! note "About `void*`"
    `void*` can hold any object address but has no type. C APIs (like `pthread_create` or JNI) use it for
    "user data". In C++ code, prefer templates or `std::function`, and when you must use `void*`,
    `static_cast` it back to the *exact* original type.
""",
files={"": r'''
#include <iostream>

struct Frame { int width; int height; };

void describe(const Frame* f) {       // pointer: may be null
    if (f == nullptr) { std::cout << "no frame\n"; return; }
    std::cout << f->width << 'x' << f->height << '\n';   // f->width == (*f).width
}

int main() {
    int level = 42;
    int* p = &level;
    *p = 7;
    std::cout << "level=" << level << '\n';

    int samples[5] = {10, 20, 30, 40, 50};
    int* first = samples;              // array decays to pointer to first element
    int* last = samples + 4;
    std::cout << "*(first+2)=" << *(first + 2) << " first[3]=" << first[3]
              << " distance=" << (last - first) << '\n';

    for (const int* it = samples; it != samples + 5; ++it)   // one-past-the-end is OK to form
        std::cout << *it << ' ';
    std::cout << '\n';

    const int* ro = &level;   // can't write through ro
    ro = &samples[0];         // but can re-point it
    int* const fixed = &level;
    *fixed = 99;              // can write, can't re-point
    std::cout << *ro << ' ' << level << '\n';

    Frame hd{1280, 720};
    describe(&hd);
    describe(nullptr);
}
'''},
takeaways=["A pointer stores an address; `*p` is the object, `&x` is the address of `x`.",
"Pointer arithmetic moves by whole elements and is only valid within one array (plus one-past-the-end).",
"Read pointer declarations right to left: `const int*` vs `int* const`.",
"Use references when there's always an object; raw pointers for optional, non-owning access."],
quiz=[("If `int a[4]` starts at address 1000 and `sizeof(int)==4`, what address is `a + 3`?", "1012 — arithmetic is in units of elements."),
("Which of these can you do with `const char* s`: `s = other;` / `*s = 'x';`?", "`s = other;` is fine (re-pointing). `*s = 'x';` is an error (the pointee is const)."),
("When would you choose a pointer parameter over a reference?", "When \"no object\" is a legitimate input (null), or for C interop. Otherwise a reference documents that an object is required."),
("Is forming the pointer `a + 4` for `int a[4]` UB? Dereferencing it?", "Forming one-past-the-end is allowed (used as an end marker); dereferencing it is UB.")]),

dict(title="Dynamic memory and a first map of undefined behaviour", std="C++20", minutes=12, area="Basics: memory",
features=[("Stack vs heap, `new`/`delete`, `new[]`/`delete[]`", "C++98"), ("Memory leaks, double free, use-after-free", "—"), ("Undefined behaviour: what it means for the optimizer", "—"), ("AddressSanitizer / UBSan first look", "—"), ("Placement new (preview)", "C++98")],
why="""
Sometimes you don't know until run time how much memory you need — a frame whose size comes from a
video header, say. That memory comes from the *heap*. C++ lets you manage it by hand with `new` and
`delete`... and this lesson is mostly about why you almost never should. Seeing the failure modes once
will make you appreciate RAII and smart pointers in the coming weeks.
""",
body="""
## Stack vs heap

- **Stack** (automatic storage): local variables. Allocation is just moving a pointer — extremely fast —
  and cleanup is automatic at the end of scope. But it's limited (often 1–8 MB per thread) and sizes are
  fixed at compile time.
- **Heap** (dynamic storage): `new` asks the allocator for memory at run time. You decide when it's freed.

```cpp
int* one = new int{5};        // allocate one int
delete one;                   // free it

int* many = new int[n]{};     // allocate n ints, zeroed
delete[] many;                // arrays need delete[]
```

## Four ways manual memory goes wrong

1. **Leak**: forget to `delete` (or an early `return`/exception skips it).
2. **Double free**: `delete` the same pointer twice.
3. **Use-after-free**: use memory after deleting it.
4. **Mismatch**: `new[]` with `delete` (or `malloc` with `delete`).

The last three are **undefined behaviour**.

## What "undefined behaviour" really means

UB doesn't mean "crashes" or "gives a random value". It means **the standard places no requirements on
the program at all**. The optimizer assumes UB never happens and transforms code accordingly. So a
single out-of-bounds read can make an unrelated `if` vanish. Common sources you've met so far:

- signed integer overflow, out-of-bounds access, null/dangling dereference,
- reading uninitialized variables, data races (Week 13), violating aliasing rules (Week 16).

We keep a full catalogue in Lesson 9.5.

## The fix: let objects own memory

Here's the modern answer. You rarely write `new` at all:

{{ex}}

`std::vector` and `std::unique_ptr` free their memory automatically when they go out of scope — even if
an exception is thrown. That's RAII, the heart of Week 4.

## Tools that catch memory bugs

Compile with **AddressSanitizer** while developing:

```bash
g++ -std=c++20 -g -fsanitize=address,undefined bug.cpp && ./a.out
```

ASan reports use-after-free, double free, out-of-bounds and leaks with a stack trace. Here's a program
with a deliberate use-after-free. Our checker runs it under ASan in CI to make sure ASan really catches it:

{{ex:_uaf}}

ASan prints something like `ERROR: AddressSanitizer: heap-use-after-free ... READ of size 4`. Android
supports ASan and HWASan too (HWASan is the recommended one on arm64).

!!! warning "Honest note"
    Valgrind and sanitizers find bugs *in the code paths you execute*. They're not proofs. Combine them
    with tests (Week 15) and with designs where ownership is obvious.
""",
files={"": r'''
#include <iostream>
#include <memory>
#include <vector>

struct Frame {
    int w, h;
    std::vector<unsigned char> pixels;
    Frame(int w_, int h_) : w(w_), h(h_), pixels(static_cast<std::size_t>(w_ * h_)) {}
};

int main() {
    // Manual (the old way): works, but every exit path must remember delete[].
    int n = 4;
    int* raw = new int[n]{};
    raw[0] = 1;
    delete[] raw;

    // Modern: containers and smart pointers own memory.
    std::vector<int> v(static_cast<std::size_t>(n));   // n zeroed ints, freed automatically
    v[0] = 1;
    auto frame = std::make_unique<Frame>(640, 480);    // heap object, freed automatically
    std::cout << "frame " << frame->w << 'x' << frame->h << " bytes=" << frame->pixels.size()
              << " v[0]=" << v[0] << '\n';
}   // frame and v cleaned up here, in reverse order
''', "_uaf": {"expect": "san-detect", "san": ["address"], "code": r'''
// Deliberately broken: use-after-free. Compile with -fsanitize=address to see the report.
#include <iostream>

int main() {
    int* p = new int{42};
    delete p;
    std::cout << *p << '\n';   // UB: heap-use-after-free
}
'''}},
takeaways=["Stack allocation is fast and automatic; heap allocation is flexible but must be freed.",
"Manual `new`/`delete` invites leaks, double frees, use-after-free and mismatched `delete[]`.",
"UB means no requirements at all; the optimizer assumes it never happens.",
"Let `std::vector` / `std::unique_ptr` own memory, and develop with `-fsanitize=address,undefined`."],
quiz=[("What's wrong with `int* p = new int[10]; delete p;`?", "Memory from `new[]` must be released with `delete[]`; using `delete` is undefined behaviour."),
("Why can't you rely on UB 'just crashing'?", "The standard imposes no requirements; the optimizer may assume UB is impossible and transform surrounding code, so the effect can be anything, including silently wrong results."),
("Which tool reports heap-use-after-free with a stack trace?", "AddressSanitizer (`-fsanitize=address`), or HWASan on arm64 Android; also Valgrind's memcheck.")]),

dict(title="Strings: C strings, std::string, and std::string_view", std="C++23", minutes=12, area="Basics: memory",
features=[("C strings (`const char*`, NUL terminator), `<cstring>` pitfalls", "C++98"), ("`std::string` basics, SSO", "C++98"), ("`std::string_view`", "C++17"), ("`starts_with` / `ends_with`", "C++20"), ("`contains`", "C++23"), ("`std::string` literals `\"x\"s` and `\"x\"sv`", "C++14"), ("Dangling string_view pitfalls", "C++17")],
why="""
Text is everywhere: file paths, log messages, codec names, JSON. C++ inherited C's strings — arrays of
`char` ending in a zero byte — and they've caused more security bugs than almost anything else. Modern
C++ gives you `std::string` to own text and `std::string_view` to look at it cheaply. Let's see when to
use which.
""",
body="""
## C strings: an array and a promise

`"hello"` is an array of 6 `const char`s: `h e l l o \\0`. Every C string function (`strlen`, `strcpy`,
`strcat`) walks until it finds that `\\0`. If it's missing, or the destination buffer is too small,
you overflow memory. `strlen` is also O(n) every time you call it.

```cpp
char buf[8];
std::strcpy(buf, "much too long");   // WRONG: buffer overflow, UB
```

## `std::string`: owns its characters

`std::string` stores its length, grows as needed, and frees its memory automatically. Short strings
(typically up to 15 characters in libstdc++, 22 in libc++) are stored *inside* the string object with no
heap allocation: the **small string optimization** (SSO).

## `std::string_view`: a window onto characters (C++17)

A `string_view` is just a pointer + length. It doesn't own anything, never allocates, and can view a
`std::string`, a C string literal, or part of either. It's the ideal type for *read-only string
parameters*:

```cpp
bool is_audio(std::string_view mime) { return mime.starts_with("audio/"); }
is_audio("audio/opus");          // no std::string created
is_audio(some_std_string);       // no copy
```

{{ex}}

## The big pitfall: string_view doesn't keep anything alive

```cpp
std::string_view codec_name() {
    std::string s = "opus";
    return s;                    // WRONG: view into a destroyed string
}
std::string_view v = std::string("tmp") + "x";   // WRONG: the temporary dies at the ';'
```

Rule: use `string_view` for parameters and short-lived local views; **return and store `std::string`**
unless you're returning a view into something that clearly outlives the caller (like a string literal or
a member).

!!! note "Also: a string_view isn't NUL-terminated"
    `sv.data()` isn't guaranteed to end in `\\0`, so don't pass it to C functions expecting a C string.
    Convert with `std::string(sv).c_str()` when calling C APIs.

We'll cover text *formatting* (`std::format`, `std::print`) and the hard truth about Unicode in Week 12.
""",
files={"": r'''
#include <cstring>
#include <iostream>
#include <string>
#include <string_view>

using namespace std::literals;   // for "..."s and "..."sv

bool is_audio(std::string_view mime) { return mime.starts_with("audio/"); }

std::string_view extension(std::string_view path) {   // returns a view INTO path: caller keeps path alive
    const auto dot = path.rfind('.');
    return dot == std::string_view::npos ? std::string_view{} : path.substr(dot + 1);
}

int main() {
    const char* c = "hello";
    std::cout << "strlen=" << std::strlen(c) << " sizeof(\"hello\")=" << sizeof("hello") << '\n';

    std::string s = "track";
    s += "-01";                       // grows as needed
    s.insert(0, "my-");
    std::cout << s << " size=" << s.size() << '\n';

    std::cout << std::boolalpha << is_audio("audio/opus") << ' ' << is_audio(std::string{"video/h264"}) << '\n';

    const std::string path = "/sdcard/Music/song.flac";
    std::cout << "ext=" << extension(path) << '\n';

    auto owned = "literal"s;        // std::string
    auto view = "literal"sv;        // std::string_view
    std::cout << owned.size() << ' ' << view.size() << ' ' << (owned == view) << '\n';
    std::cout << "contains 'song'? " << path.contains("song") << '\n';   // C++23
}
'''},
takeaways=["C strings rely on a terminating `\\0`; `strcpy`-style functions easily overflow.",
"`std::string` owns and manages text; short strings avoid heap allocation (SSO).",
"Take read-only text parameters as `std::string_view`.",
"Never return or store a `string_view` to something that may die first."],
quiz=[("What is `sizeof(\"abc\")`?", "4: three characters plus the terminating `\\0`."),
("Why is `std::string_view` a good parameter type but a risky member/return type?", "As a parameter it avoids copies and accepts any string type, and the argument outlives the call. As a return/member it may outlive the characters it views, producing a dangling view."),
("Can you pass `sv.data()` to `fopen`?", "Not safely: a string_view's data isn't guaranteed to be NUL-terminated. Make a `std::string` first.")]),

dict(title="Bits and bytes: bitwise operators, std::byte, and <bit>", std="C++23", minutes=11, area="Basics: memory",
features=[("Bitwise operators `& | ^ ~ << >>`, masks", "C++98"), ("Shift pitfalls (shifting by >= width is UB; negative values)", "C++20"), ("`std::byte`", "C++17"), ("`<bit>`: popcount, countl_zero, rotl, bit_ceil, has_single_bit", "C++20"), ("`std::bit_cast`", "C++20"), ("`std::endian`, `std::byteswap`", "C++23"), ("Two's complement guaranteed", "C++20")],
why="""
An H.264 NAL unit header packs three fields into a single byte: 1 bit, 2 bits and 5 bits. Hardware
registers, flags, compression, hashing — all of it is bit twiddling. C++ gives you direct access to bits,
and C++20 finally added a proper `<bit>` header so you no longer need compiler-specific builtins. Let's
decode that header.
""",
body="""
## The operators

| Op | Meaning | Typical use |
|---|---|---|
| `a & b` | AND | test/clear bits with a mask |
| `a \\| b` | OR | set bits |
| `a ^ b` | XOR | toggle bits |
| `~a` | NOT | invert (build "clear" masks) |
| `a << n`, `a >> n` | shift | move fields into place |

Extracting a field = **shift it down, then mask it**: `(byte >> 5) & 0b11` gives bits 5–6.

## Pitfalls

- Shifting by a count `>=` the width of the (promoted) type is **UB**: `1u << 32` on a 32-bit `unsigned`.
- `1 << 31` on `int`: before C++20 this was UB; since C++20 signed integers are defined to be two's
  complement and left shift is well-defined — but stick to **unsigned types** for bit manipulation anyway.
- Remember integer promotion: `~std::uint8_t{0x0F}` is an `int` `0xFFFFFFF0`, not `0xF0`.

## `std::byte` (C++17)

`std::byte` is "a byte of raw memory", not a character and not a number. It only supports bitwise ops,
so you can't accidentally do arithmetic on it. Use `std::to_integer<int>(b)` to read it.

## `<bit>` (C++20)

Portable versions of things you used to need intrinsics for: `std::popcount`, `std::countl_zero`,
`std::countr_zero`, `std::rotl`/`rotr`, `std::has_single_bit` (power of two?), `std::bit_ceil`,
`std::bit_width`, and `std::bit_cast` — the *safe* way to reinterpret an object's bits as another type of
the same size. C++23 added `std::byteswap`, and `std::endian` (C++20) tells you the platform byte order.

{{ex}}

## The wrong way to reinterpret bits

```cpp
float f = 1.0f;
std::uint32_t u = *reinterpret_cast<std::uint32_t*>(&f);   // WRONG: violates strict aliasing (UB)
std::uint32_t ok = std::bit_cast<std::uint32_t>(f);          // right (C++20); or std::memcpy
```

!!! tip "Pro tip: ring buffers love powers of two"
    If a buffer's capacity is a power of two, `index & (capacity - 1)` replaces the slower
    `index % capacity`. You'll use exactly this in the embedded capstone.
""",
files={"": r'''
#include <bit>
#include <bitset>
#include <cstddef>
#include <cstdint>
#include <iostream>

struct NalHeader { unsigned forbidden, ref_idc, type; };

NalHeader parse(std::uint8_t b) {
    return {static_cast<unsigned>(b >> 7) & 0x1u,
            static_cast<unsigned>(b >> 5) & 0x3u,
            static_cast<unsigned>(b) & 0x1Fu};
}

int main() {
    const std::uint8_t nal = 0x67;   // a typical H.264 SPS header byte
    const auto h = parse(nal);
    std::cout << "bits=" << std::bitset<8>(nal) << " forbidden=" << h.forbidden
              << " ref_idc=" << h.ref_idc << " type=" << h.type << '\n';

    unsigned flags = 0;
    flags |= 1u << 3;        // set bit 3
    flags |= 1u << 0;        // set bit 0
    flags &= ~(1u << 0);     // clear bit 0
    flags ^= 1u << 5;        // toggle bit 5
    std::cout << "flags=" << std::bitset<8>(flags) << " popcount=" << std::popcount(flags) << '\n';

    std::cout << "bit_ceil(600)=" << std::bit_ceil(600u) << " has_single_bit(512)=" << std::has_single_bit(512u)
              << " countr_zero(40)=" << std::countr_zero(40u) << '\n';

    std::cout << std::hex << "bits of 1.0f = 0x" << std::bit_cast<std::uint32_t>(1.0f)
              << " byteswap(0x11223344)=0x" << std::byteswap(0x11223344u) << std::dec << '\n';
    std::cout << "little endian? " << (std::endian::native == std::endian::little) << '\n';

    std::byte b{0b1010'0000};
    b |= std::byte{0x01};
    std::cout << "std::byte as int: " << std::to_integer<int>(b) << '\n';
}
'''},
takeaways=["Extract a bit field with shift-then-mask; use unsigned types for bit manipulation.",
"Shifting by >= the type width is UB; watch integer promotion with `~` on small types.",
"`std::byte` is raw memory, not a number; `<bit>` gives portable popcount, rotations, `bit_cast` etc.",
"Use `std::bit_cast` or `memcpy`, never `reinterpret_cast`, to reinterpret an object's bits."],
quiz=[("How do you extract bits 2..4 (3 bits) of `x`?", "`(x >> 2) & 0b111`."),
("What is the type and value of `~std::uint8_t{0}`?", "`int`, value `-1` (all bits set), due to integer promotion before `~`."),
("Why is `*reinterpret_cast<int*>(&some_float)` wrong?", "It violates the strict aliasing rule (accessing a float object through an int glvalue), which is UB. Use `std::bit_cast<int>(f)` or `std::memcpy`."),
("What does `std::has_single_bit(x)` tell you?", "Whether `x` is a power of two.")]),
],
assignment=dict(title="A bit-packed sensor record", task="""
A sensor sends 32-bit records: bits 0–11 are a temperature reading (unsigned, 0.1°C steps with an offset of
-40°C), bits 12–19 humidity (percent), bits 20–27 a sensor id, bits 28–31 flags.

1. Write `constexpr std::uint32_t pack(...)` and `Record unpack(std::uint32_t)`.
2. Take a `std::span<const std::uint32_t>` of records and print each one.
3. Report how many records have flag bit 0 set, using `std::popcount` or masks.
4. No raw `new`, no C strings, no `reinterpret_cast`.
""", solution=r'''
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <span>

struct Record { double temp_c; unsigned humidity, id, flags; };

constexpr std::uint32_t pack(double temp_c, unsigned humidity, unsigned id, unsigned flags) {
    const auto raw_t = static_cast<std::uint32_t>((temp_c + 40.0) * 10.0 + 0.5) & 0xFFFu;
    return raw_t | (std::uint32_t{humidity & 0xFFu} << 12) | (std::uint32_t{id & 0xFFu} << 20)
           | (std::uint32_t{flags & 0xFu} << 28);
}

Record unpack(std::uint32_t r) {
    return {static_cast<double>(r & 0xFFFu) / 10.0 - 40.0, (r >> 12) & 0xFFu, (r >> 20) & 0xFFu, (r >> 28) & 0xFu};
}

int count_flag0(std::span<const std::uint32_t> recs) {
    int n = 0;
    for (auto r : recs) n += static_cast<int>((r >> 28) & 1u);
    return n;
}

int main() {
    constexpr std::array<std::uint32_t, 3> recs{pack(21.5, 40, 7, 0b0001), pack(-5.0, 85, 8, 0b0010),
                                                pack(36.6, 55, 9, 0b1001)};
    static_assert(pack(0.0, 0, 0, 0) == 400);   // checked at compile time
    for (auto r : recs) {
        const auto x = unpack(r);
        std::cout << "id=" << x.id << " temp=" << x.temp_c << "C hum=" << x.humidity
                  << "% flags=" << x.flags << " (" << std::popcount(x.flags) << " set)\n";
    }
    std::cout << "flag0 set in " << count_flag0(recs) << " records\n";
}
'''))
