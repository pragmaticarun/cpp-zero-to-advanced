WEEK = dict(num=12, title="The standard library III: memory, text, files, and time", intro="""
This week covers the parts of the standard library you'll touch in every real program: smart pointers
and allocators for memory, `std::format`/`std::print` for text, `<filesystem>` for files, `<chrono>` for
time, plus a tour of the remaining utility headers. Lots of APIs, so we focus on idioms and pitfalls.
""", lessons=[
dict(title="unique_ptr and custom deleters", std="C++20", minutes=11, area="Memory management",
features=[("`std::unique_ptr`, `std::make_unique`", "C++11/14"), ("`unique_ptr<T[]>`", "C++11"), ("Custom deleters (function objects, lambdas, function pointers)", "C++11"), ("Ownership transfer via move; `release`, `reset`, `get`", "C++11"), ("`std::make_unique_for_overwrite`", "C++20"), ("`std::out_ptr`, `std::inout_ptr`", "C++23"), ("Smart pointer parameter guidelines", "—")],
why="""
Back in Week 3 we saw how raw `new`/`delete` leaks and double-frees. `std::unique_ptr` fixes that with
*zero* overhead: it's exactly one pointer, and its destructor calls `delete`. With a custom deleter it
manages *any* resource — `FILE*`, a codec handle from a C library, an OpenGL texture. It should be your
default for owning heap objects.
""",
body="""
## Unique ownership

```cpp
auto codec = std::make_unique<Codec>(48000);   // owns the Codec
auto other = std::move(codec);                 // ownership transferred; codec is now null
```

`unique_ptr` is move-only, so "who owns this" is visible in the code: you can't accidentally share it.

## Custom deleters for C resources

```cpp
struct FileCloser { void operator()(std::FILE* f) const noexcept { std::fclose(f); } };
using File = std::unique_ptr<std::FILE, FileCloser>;
```

A stateless function-object deleter keeps `sizeof(File) == sizeof(FILE*)`. A function-pointer deleter
adds a pointer's worth of size. C++23's `std::out_ptr` adapts a `unique_ptr` to C APIs that return a
resource through a `T**` out-parameter.

{{ex}}

## Passing smart pointers (C++ Core Guidelines R.30–R.37)

| You want to... | Parameter type |
|---|---|
| just use the object | `T&` or `T*` (nullable) — **not** a smart pointer |
| take ownership | `std::unique_ptr<T>` by value |
| maybe reseat the caller's pointer | `std::unique_ptr<T>&` |
| share ownership | `std::shared_ptr<T>` by value |

## Pitfalls

- Two `unique_ptr`s from the same raw pointer → double free.
- `unique_ptr<T>` for an array allocated with `new[]` → use `unique_ptr<T[]>` (or better, `std::vector`).
- `release()` gives up ownership *without* deleting — the caller must now free it.
""",
files={"": r'''
#include <cstdio>
#include <iostream>
#include <memory>
#include <string>
#include <utility>

struct Codec {
    explicit Codec(int rate) : rate{rate} { std::cout << "  Codec(" << rate << ") opened\n"; }
    ~Codec() { std::cout << "  Codec(" << rate << ") closed\n"; }
    int rate;
};

struct FileCloser { void operator()(std::FILE* f) const noexcept { if (f) { std::fclose(f); std::cout << "  file closed\n"; } } };
using File = std::unique_ptr<std::FILE, FileCloser>;

// A C-style API that returns a resource through an out-parameter
int c_open_codec(int rate, Codec** out) { *out = new Codec{rate}; return 0; }

void use(const Codec& c) { std::cout << "  using codec at " << c.rate << '\n'; }      // borrows
void sink(std::unique_ptr<Codec> c) { std::cout << "  sink took " << c->rate << '\n'; } // takes ownership

int main() {
    {
        auto a = std::make_unique<Codec>(44100);
        use(*a);
        auto b = std::move(a);                                   // transfer
        std::cout << "  a is " << (a ? "set" : "null") << '\n';
        sink(std::move(b));                                      // destroyed at the end of sink
        std::cout << "after sink\n";
    }
    {
        File f{std::tmpfile()};
        std::fputs("hello", f.get());
        std::cout << "  sizeof(File)==sizeof(FILE*)? " << std::boolalpha << (sizeof(File) == sizeof(std::FILE*)) << '\n';
    }
    {
        std::unique_ptr<Codec> c;
        c_open_codec(96000, std::out_ptr(c));                    // C++23
        std::cout << "  out_ptr filled codec at " << c->rate << '\n';
    }
    auto buf = std::make_unique_for_overwrite<char[]>(4096);    // no zeroing: we'll overwrite it
    buf[0] = 'x';
    std::cout << "buffer starts with " << buf[0] << '\n';
}
''', "std": "c++23", "maybe_unsupported": True},
takeaways=["`unique_ptr` is zero-overhead exclusive ownership; transfer it with `std::move`.",
"Custom deleters manage any resource; stateless deleters add no size.",
"Pass `T&`/`T*` to functions that only use an object; pass `unique_ptr` by value to transfer ownership.",
"`std::out_ptr` (C++23) bridges smart pointers and C out-parameter APIs."],
quiz=[("What's `sizeof(std::unique_ptr<int>)` on a typical 64-bit platform?", "8 bytes — the same as a raw pointer (with the default deleter)."),
("How should a function that only reads a `Codec` take it?", "By `const Codec&` (or `const Codec*` if null is allowed), not by smart pointer."),
("What does `release()` do?", "Returns the raw pointer and sets the unique_ptr to null without deleting; the caller becomes responsible for freeing it.")]),

dict(title="shared_ptr, weak_ptr, and ownership graphs", std="C++20", minutes=11, area="Memory management",
features=[("`std::shared_ptr`, `std::make_shared`", "C++11"), ("Control block and reference counts", "C++11"), ("`std::weak_ptr`, `lock()`, breaking cycles", "C++11"), ("`std::enable_shared_from_this`", "C++11"), ("Aliasing constructor", "C++11"), ("`std::atomic<std::shared_ptr>`", "C++20"), ("`make_shared` for arrays", "C++20")],
why="""
Sometimes ownership really is shared: an audio buffer used by the player *and* the waveform view, and it
should live as long as either needs it. `std::shared_ptr` counts owners and frees the object when the last
one goes. It's convenient — and easy to overuse. Let's learn the cost, the cycle trap, and `weak_ptr`.
""",
body="""
## How it works

A `shared_ptr` is two pointers: one to the object, one to a **control block** holding the strong count,
weak count and deleter. Copying increments the strong count *atomically* (thread-safe counting, not
thread-safe object access). `make_shared` allocates object and control block together: one allocation,
better locality.

## The cycle trap

```cpp
struct Node { std::shared_ptr<Node> next; std::shared_ptr<Node> prev; };   // a <-> b
```

If `a.next = b` and `b.prev = a`, neither count reaches zero — leak. Make the back-edge a
**`std::weak_ptr`**: it observes without owning. Call `lock()` to get a temporary `shared_ptr` (null if the
object is gone).

{{ex}}

## `enable_shared_from_this`

Inside a member function you sometimes need a `shared_ptr` to `this` (e.g. to register a callback that
keeps the object alive). Creating `std::shared_ptr<T>(this)` makes a *second* control block → double
delete. Inherit `std::enable_shared_from_this<T>` and call `shared_from_this()` instead.

## Guidelines

- Prefer `unique_ptr`; reach for `shared_ptr` only for genuinely shared lifetime. A `unique_ptr` converts to
  a `shared_ptr` later if needed.
- Don't pass `shared_ptr` by value "just in case" — each copy is an atomic increment and decrement.
- The aliasing constructor shares ownership of an object while pointing to one of its members.
""",
files={"": r'''
#include <iostream>
#include <memory>
#include <string>
#include <vector>

struct Buffer {
    std::string name;
    explicit Buffer(std::string n) : name{std::move(n)} {}
    ~Buffer() { std::cout << "  ~Buffer(" << name << ")\n"; }
};

struct Track;
struct Album {
    std::vector<std::shared_ptr<Track>> tracks;     // owns tracks
    ~Album() { std::cout << "  ~Album\n"; }
};
struct Track {
    std::weak_ptr<Album> album;                     // back-edge: observes, doesn't own
    ~Track() { std::cout << "  ~Track\n"; }
};

class Session : public std::enable_shared_from_this<Session> {
public:
    std::shared_ptr<Session> self() { return shared_from_this(); }
};

int main() {
    {
        auto buf = std::make_shared<Buffer>("pcm");
        auto view = buf;                            // second owner
        std::cout << "use_count=" << buf.use_count() << '\n';
        buf.reset();
        std::cout << "after reset, view still alive: " << view->name << '\n';
    }
    std::cout << "--- album with weak back-edges\n";
    {
        auto album = std::make_shared<Album>();
        auto t = std::make_shared<Track>();
        t->album = album;
        album->tracks.push_back(t);
        if (auto a = t->album.lock()) std::cout << "  track's album has " << a->tracks.size() << " track(s)\n";
    }                                               // everything freed: no cycle
    std::cout << "--- weak_ptr expiry\n";
    std::weak_ptr<Buffer> watcher;
    {
        auto b = std::make_shared<Buffer>("temp");
        watcher = b;
        std::cout << "  expired? " << std::boolalpha << watcher.expired() << '\n';
    }
    std::cout << "  expired? " << watcher.expired() << '\n';

    auto s = std::make_shared<Session>();
    auto s2 = s->self();
    std::cout << "session owners: " << s.use_count() << '\n';

    struct Pair { int a = 1; int b = 2; };
    auto p = std::make_shared<Pair>();
    std::shared_ptr<int> just_b(p, &p->b);          // aliasing: shares p's ownership
    p.reset();
    std::cout << "aliased member still valid: " << *just_b << '\n';
}
'''},
takeaways=["`shared_ptr` = object pointer + control block with atomic counts; `make_shared` allocates once.",
"Cycles of `shared_ptr` leak; use `weak_ptr` for back-edges and `lock()` to access.",
"Use `enable_shared_from_this` instead of `shared_ptr<T>(this)`.",
"Prefer `unique_ptr`; don't pass `shared_ptr` by value unless you're sharing ownership."],
quiz=[("Is `shared_ptr` thread-safe?", "The reference counting is (atomic); accessing the pointed-to object or assigning to the same shared_ptr instance from several threads is not (use `std::atomic<std::shared_ptr<T>>` for the latter)."),
("How does `weak_ptr` break a cycle?", "It doesn't contribute to the strong count, so the objects can be destroyed when external owners go away."),
("What goes wrong with `return std::shared_ptr<Session>(this);`?", "It creates a second, independent control block; both will delete the object — double free.")]),

dict(title="Allocators and polymorphic memory resources (pmr)", std="C++20", minutes=11, area="Memory management",
features=[("Allocator model (`std::allocator`, `allocator_traits`)", "C++98/11"), ("`std::pmr::memory_resource`, `polymorphic_allocator`", "C++17"), ("`monotonic_buffer_resource`, `unsynchronized_pool_resource`, `synchronized_pool_resource`", "C++17"), ("`std::pmr::vector`, `std::pmr::string`", "C++17"), ("Custom `operator new`/`delete` overloads", "C++98"), ("Aligned allocation (`align_val_t`)", "C++17")],
why="""
In a real-time audio callback you're not allowed to call `malloc` — it may take a lock and blow your 2 ms
deadline. In a game, you want all per-frame allocations to come from one arena that's reset each frame.
Allocators let you keep using `std::vector` and `std::string` while controlling *where* their memory comes
from. C++17's `pmr` makes this practical.
""",
body="""
## Classic allocators — and why they were painful

Containers take an allocator template parameter: `std::vector<int, MyAlloc<int>>`. But the allocator is
part of the *type*, so a `vector<int, A>` can't be passed where `vector<int>` is expected. That limited
their use.

## `std::pmr` (C++17)

`std::pmr::polymorphic_allocator` holds a pointer to a `std::pmr::memory_resource` and forwards to it via
virtual calls. `std::pmr::vector<int>` is one type regardless of the resource. The standard resources:

| Resource | Behaviour |
|---|---|
| `monotonic_buffer_resource` | bump-pointer arena; `deallocate` is a no-op; free all at once. Very fast. |
| `unsynchronized_pool_resource` | pools of fixed-size blocks; single-threaded |
| `synchronized_pool_resource` | same, thread-safe |
| `new_delete_resource()` | the global heap |
| `null_memory_resource()` | throws on any allocation — great as an upstream to *prove* you never hit the heap |

{{ex}}

The example builds a vector of strings inside a stack buffer and proves no heap allocation happens by
using `null_memory_resource()` as the fallback. Note that `pmr` containers propagate the allocator to
their elements (`pmr::string` inside `pmr::vector` uses the same arena).

## Replacing global `operator new`

You can replace `operator new`/`operator delete` globally to count or trace allocations — useful in tests
("this function must not allocate"). The example counts global allocations.

!!! warning "Pitfall"
    A monotonic arena never reuses memory until it's destroyed or `release()`d. Great for per-frame or
    per-request work; bad for long-lived containers that grow and shrink.
""",
files={"": r'''
#include <array>
#include <cstddef>
#include <cstdlib>
#include <iostream>
#include <memory_resource>
#include <new>
#include <string>
#include <vector>

static std::size_t g_allocs = 0;
void* operator new(std::size_t n) {                     // replaced global operator new: count calls
    ++g_allocs;
    if (void* p = std::malloc(n ? n : 1)) return p;
    throw std::bad_alloc{};
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }

int main() {
    std::size_t before = g_allocs;
    {
        std::vector<std::string> v;
        for (int i = 0; i < 4; ++i) v.push_back("a fairly long string number " + std::to_string(i));
    }
    std::cout << "std::vector<std::string>: " << (g_allocs - before > 0 ? "heap allocations happened" : "no heap") << '\n';

    alignas(std::max_align_t) std::array<std::byte, 4096> stack_buf;
    before = g_allocs;
    {
        std::pmr::monotonic_buffer_resource arena{stack_buf.data(), stack_buf.size(), std::pmr::null_memory_resource()};
        std::pmr::vector<std::pmr::string> v{&arena};
        v.reserve(4);
        for (int i = 0; i < 4; ++i) {
            std::pmr::string s{"a fairly long string number ", &arena};
            s += static_cast<char>('0' + i);
            v.push_back(std::move(s));
        }
        std::cout << "pmr in arena: " << v.size() << " strings, last = \"" << v.back() << "\"\n";
        std::cout << "element uses the same arena? " << std::boolalpha
                  << (v.back().get_allocator().resource() == &arena) << '\n';
    }
    std::cout << "global allocations during pmr block: " << (g_allocs - before) << '\n';

    try {
        std::array<std::byte, 16> tiny;
        std::pmr::monotonic_buffer_resource small{tiny.data(), tiny.size(), std::pmr::null_memory_resource()};
        std::pmr::vector<int> v{&small};
        v.resize(100);                                   // needs more than 16 bytes
    } catch (const std::bad_alloc&) {
        std::cout << "null_memory_resource caught an overflow of the arena\n";
    }
}
'''},
takeaways=["Allocators control where container memory comes from; classic ones are part of the type.",
"`std::pmr` containers share one type and take a `memory_resource*` at run time.",
"`monotonic_buffer_resource` is a fast arena; `null_memory_resource` proves no heap fallback.",
"Replacing global `operator new` lets tests count or forbid allocations."],
quiz=[("Why can't you pass `std::vector<int, MyAlloc<int>>` to a function taking `const std::vector<int>&`?", "The allocator is a template parameter, so they're different types."),
("What does `deallocate` do on a `monotonic_buffer_resource`?", "Nothing — memory is only reclaimed when the resource is released or destroyed."),
("Why use `null_memory_resource()` as an upstream?", "Any allocation that doesn't fit the buffer throws `bad_alloc` instead of silently using the heap, proving the code stays within the arena.")]),

dict(title="Text: std::format, std::print, iostreams, charconv, and Unicode", std="C++23", minutes=13, area="Standard library: text & I/O",
features=[("`std::format`, format specifications", "C++20"), ("`std::print`, `std::println`", "C++23"), ("Custom `std::formatter` specializations", "C++20"), ("Formatting ranges", "C++23"), ("iostreams, manipulators, `std::stringstream`", "C++98"), ("`std::from_chars` / `std::to_chars`", "C++17"), ("`char8_t`, UTF-8 string literals", "C++20"), ("`std::format` compile-time format string checks", "C++20")],
why="""
Printing a table of meter readings with aligned columns used to mean either `printf` (fast, type-unsafe) or
iostreams (type-safe, verbose, slow, stateful). C++20's `std::format` and C++23's `std::print` give you
Python-style formatting that's type-safe, checked at compile time, and fast. We'll also cover the
fastest number parsing in the library (`from_chars`) and the state of Unicode.
""",
body="""
## `std::format` and `std::print`

```cpp
std::println("{:<10} {:>8.2f} dB", name, level);    // left-align 10, right-align 8 with 2 decimals
```

Format spec mini-language: `{index:fill align sign # 0 width .precision type}`. Examples: `{:08.3f}`, `{:#x}`,
`{:^20}`, `{:+}`. The format string is checked **at compile time**: a mismatch like `{:d}` with a string is a
compile error. For runtime format strings use `std::vformat` / `std::runtime_format` (C++26).

C++23 formats ranges too: `std::println("{}", vec)` prints `[1, 2, 3]`.

## Custom types

Specialize `std::formatter<T>`: implement `parse` (or inherit from an existing formatter) and `format`.

{{ex}}

## iostreams: still everywhere

You'll still use `std::cout`, `std::ifstream` and `std::stringstream`. Know their pitfalls: manipulators
like `std::hex` and `std::setprecision` are *sticky* (they stay set), `std::endl` flushes (slow in loops —
use `'\\n'`), and `std::ios::sync_with_stdio(false)` speeds up console I/O when you don't mix with C stdio.

## `from_chars` / `to_chars`

Locale-independent, non-allocating, non-throwing, and the fastest conversions available. Always check the
returned `ec` *and* the end pointer.

## Unicode: the honest version

`std::string` holds bytes; it doesn't know about characters. `u8"..."` literals are `char8_t` (C++20),
which doesn't convert implicitly to `char`. `size()` counts bytes, not characters. For real text processing
(normalization, case folding, grapheme clusters) use a library such as ICU. `std::print` writes UTF-8
correctly to Unicode-capable terminals, which iostreams on Windows historically did not.
""",
files={"": r'''
#include <charconv>
#include <format>
#include <iomanip>
#include <iostream>
#include <print>
#include <ranges>
#include <sstream>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

struct Level { double db; };

template <>
struct std::formatter<Level> : std::formatter<double> {        // reuse double's spec parsing
    auto format(const Level& l, std::format_context& ctx) const {
        auto out = std::formatter<double>::format(l.db, ctx);
        return std::format_to(out, " dB");
    }
};

int main() {
    std::println("{:<8}|{:>8}|{:^8}|", "left", "right", "mid");
    std::println("{:08.3f} {:+d} {:#x} {:#b} {:e}", 3.14159, 42, 255, 5, 12345.678);
    std::println("{1} before {0}", "world", "hello");
    std::println("{:>10.1f}", Level{-3.25});
    std::vector<int> v{1, 2, 3};
#if defined(__cpp_lib_format_ranges)
    std::println("ranges: {}", v);                  // C++23 range formatting (GCC 15+, Clang 16+)
#else
    std::println("ranges: [{}, {}, {}]", v[0], v[1], v[2]);   // fallback for GCC 14
#endif
    std::string s = std::format("{}-{:03}", "take", 7);
    std::cout << s << '\n';

    std::cout << std::hex << 255 << ' ' << 16 << std::dec << ' ' << 16 << '\n';   // hex was sticky
    std::cout << std::fixed << std::setprecision(2) << 2.0 / 3 << '\n';
    std::cout.unsetf(std::ios::floatfield);

    std::istringstream in{"48000 2 stereo"};
    int rate = 0, ch = 0; std::string mode;
    in >> rate >> ch >> mode;
    std::cout << rate << '/' << ch << '/' << mode << '\n';

    std::string_view text = "1234abc";
    int value = 0;
    auto [ptr, ec] = std::from_chars(text.data(), text.data() + text.size(), value);
    std::cout << "parsed " << value << ", stopped at '" << ptr << "', ok=" << (ec == std::errc{}) << '\n';
    char buf[32];
    auto res = std::to_chars(buf, buf + sizeof buf, 0.1 + 0.2);       // shortest round-trip repr
    std::cout << "to_chars(0.1+0.2) = " << std::string_view(buf, static_cast<std::size_t>(res.ptr - buf)) << '\n';

    std::u8string_view word = u8"caf\u00e9";
    std::cout << "u8\"cafe-acute\" has " << word.size() << " bytes for 4 characters\n";
}
''', "std": "c++23"},
takeaways=["`std::format`/`std::println` give type-safe, compile-time-checked, Python-style formatting.",
"Specialize `std::formatter<T>` (often by inheriting an existing one) for your types.",
"iostream manipulators are sticky; prefer `'\\n'` over `std::endl` in loops.",
"`from_chars`/`to_chars` are the fastest, locale-free conversions; `std::string` is bytes, not characters."],
quiz=[("What happens if you write `std::format(\"{:d}\", std::string{\"x\"})`?", "A compile-time error: the format string is checked against the argument types."),
("Why can `std::endl` make output slow?", "It flushes the stream every time; in a loop that defeats buffering."),
("How many bytes does `u8\"é\"` (one character, U+00E9) use, excluding the terminator?", "Two bytes in UTF-8.")]),

dict(title="std::filesystem", std="C++20", minutes=10, area="Standard library: files",
features=[("`std::filesystem::path` operations", "C++17"), ("`directory_iterator`, `recursive_directory_iterator`", "C++17"), ("`create_directories`, `copy`, `rename`, `remove_all`", "C++17"), ("`file_size`, `last_write_time`, `status`, `exists`", "C++17"), ("Error handling: `filesystem_error` vs `error_code` overloads", "C++17"), ("File I/O with `std::ifstream`/`ofstream`, binary mode", "C++98")],
why="""
Batch-converting a folder of WAV files, cleaning up old logs, finding every `.json` preset under a
directory — before C++17 these needed POSIX or Win32 calls. `std::filesystem` makes them portable. It also
has a few sharp edges around errors and races that we'll point out.
""",
body="""
## Paths

`std::filesystem::path` handles separators and pieces: `p / "sub" / "file.wav"`, `p.filename()`,
`p.stem()`, `p.extension()`, `p.parent_path()`, `p.replace_extension(".flac")`. It's just a string
manipulation type — a path doesn't have to exist.

## Walking directories

`directory_iterator` lists one directory; `recursive_directory_iterator` walks the tree. Iteration order is
**unspecified** — sort if you need determinism.

{{ex}}

## Errors

Almost every function has two overloads: one throws `std::filesystem::filesystem_error`, one takes
`std::error_code&` (Week 9). Use the `error_code` form when failure is expected (e.g. "delete if exists").

## The TOCTOU trap

```cpp
if (fs::exists(p)) fs::remove(p);   // another process may delete p in between ("time of check to time of use")
```

Just do the operation and handle the error: `fs::remove(p, ec);`. Filesystems are shared, concurrent state.

## Reading and writing files

`std::ofstream out{path, std::ios::binary}` / `std::ifstream`. Streams don't throw by default — check
`if (!in)` or enable exceptions with `in.exceptions(...)`. For a whole file:
`std::string data{std::istreambuf_iterator<char>{in}, {}};`.
""",
files={"": r'''
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <system_error>
#include <vector>

namespace fs = std::filesystem;

int main() {
    const fs::path root = fs::temp_directory_path() / "cpp_course_fs_demo";
    fs::remove_all(root);                                          // start clean
    fs::create_directories(root / "presets" / "drums");

    for (const char* name : {"presets/kick.json", "presets/drums/snare.json", "presets/readme.txt"}) {
        std::ofstream out{root / name, std::ios::binary};
        out << "{\"name\": \"" << fs::path{name}.stem().string() << "\"}";
    }

    fs::path p = root / "presets" / "kick.json";
    std::cout << "filename=" << p.filename() << " stem=" << p.stem() << " ext=" << p.extension() << '\n';
    std::cout << "as flac: " << fs::path{p}.replace_extension(".flac").filename() << '\n';

    std::vector<std::string> found;
    for (const auto& entry : fs::recursive_directory_iterator(root))
        if (entry.is_regular_file() && entry.path().extension() == ".json")
            found.push_back(fs::relative(entry.path(), root).generic_string());
    std::ranges::sort(found);                                       // iteration order is unspecified
    for (const auto& f : found) std::cout << "json: " << f << '\n';

    std::ifstream in{p, std::ios::binary};
    std::string content{std::istreambuf_iterator<char>{in}, {}};
    std::cout << "content: " << content << " (" << fs::file_size(p) << " bytes)\n";

    std::error_code ec;
    fs::remove(root / "does-not-exist.txt", ec);                    // no TOCTOU, no exception
    std::cout << "remove missing file -> error? " << std::boolalpha << static_cast<bool>(ec) << '\n';
    fs::rename(root / "presets" / "readme.txt", root / "README.txt");
    std::cout << "renamed exists: " << fs::exists(root / "README.txt") << '\n';
    std::cout << "removed " << fs::remove_all(root) << " entries\n";
}
'''},
takeaways=["`fs::path` composes and dissects paths portably; it doesn't need to exist.",
"Directory iteration order is unspecified; sort when you need determinism.",
"Use `error_code` overloads when failure is normal; avoid check-then-act (TOCTOU) races.",
"Streams don't throw by default — check their state."],
quiz=[("What's wrong with `if (fs::exists(p)) fs::remove(p);`?", "A race: the file can change between the check and the removal; just call `fs::remove(p, ec)` and inspect `ec`."),
("Does `recursive_directory_iterator` visit files in alphabetical order?", "Not necessarily — the order is unspecified."),
("What does `fs::remove` (error_code overload) report for a missing file?", "It returns false and leaves `ec` clear — a missing file isn't an error for `remove`.")]),

dict(title="std::chrono: durations, clocks, calendars, and time zones", std="C++20", minutes=12, area="Standard library: time",
features=[("`duration`, `time_point`, `duration_cast`", "C++11"), ("Clocks: `steady_clock`, `system_clock`, `high_resolution_clock`", "C++11"), ("Duration literals (`ms`, `s`, `h`)", "C++14"), ("`floor`, `ceil`, `round` for durations", "C++17"), ("Calendar types: `year_month_day`, `weekday`, `sys_days`", "C++20"), ("Time zones: `zoned_time`, `tzdb`", "C++20"), ("Formatting chrono types with `std::format`", "C++20")],
why="""
"Wait 50 ms." "How long did encoding take?" "What's the date three months from now?" "What time is this
UTC timestamp in India?" Getting time wrong produces subtle bugs: mixing up seconds and milliseconds, using a
wall clock that jumps for measuring intervals, or doing time-zone math by hand. `<chrono>` makes units part
of the type, so many of those bugs become compile errors.
""",
body="""
## Durations carry units

```cpp
using namespace std::chrono_literals;
auto timeout = 250ms;
std::chrono::seconds s = 3min;          // OK: lossless conversion is implicit
std::chrono::seconds t = 1500ms;        // compile error: lossy! use duration_cast/floor/round
```

## Pick the right clock

| Clock | Use for |
|---|---|
| `steady_clock` | measuring intervals and timeouts (never goes backwards) |
| `system_clock` | wall-clock time, timestamps, dates |
| `high_resolution_clock` | usually an alias of one of the above — don't rely on it |

## Calendars and time zones (C++20)

`2026y/std::chrono::March/31` is a `year_month_day`. Adding months to the 31st gives an *invalid* date that
you must handle explicitly (clamp to last day, or overflow into the next month) — chrono makes you choose.
`zoned_time` converts between UTC and IANA time zones using the time-zone database.

{{ex}}

Time-zone support needs the tz database at run time and library support (GCC 14 and MSVC have it;
libc++ support is recent/partial), so that part is a separate example marked "may be unsupported":

{{ex:_tz}}

!!! tip "Pro tip"
    Store and transmit timestamps in UTC (`system_clock` / `sys_seconds`); convert to local time zones only
    for display.
""",
files={"": r'''
#include <chrono>
#include <format>
#include <iostream>
#include <thread>

int main() {
    using namespace std::chrono;
    using namespace std::chrono_literals;

    auto timeout = 250ms;
    seconds s = 3min;                                       // lossless: implicit
    auto t = duration_cast<seconds>(1500ms);                 // lossy: explicit (truncates)
    std::cout << timeout.count() << "ms, " << s.count() << "s, " << t.count() << "s, round="
              << round<seconds>(1500ms).count() << "s\n";
    std::cout << std::format("{} + {} = {}\n", 1h, 30min, 1h + 30min);

    auto start = steady_clock::now();
    std::this_thread::sleep_for(20ms);
    auto elapsed = duration_cast<milliseconds>(steady_clock::now() - start);
    std::cout << "slept at least 20ms? " << std::boolalpha << (elapsed >= 20ms) << '\n';

    year_month_day release = 2026y / January / 31;
    auto next_month = release + months{1};                   // 2026-02-31: not a valid date
    std::cout << "valid? " << next_month.ok() << '\n';
    auto clamped = next_month.year() / next_month.month() / last;
    std::cout << "clamped to " << year_month_day{clamped} << '\n';
    auto overflowed = year_month_day{sys_days{next_month}};  // normalizes into March
    std::cout << "overflowed to " << overflowed << '\n';
    std::cout << "weekday of 2026-11-03: " << weekday{sys_days{2026y / November / 3}} << '\n';
    auto days_left = sys_days{2026y / December / 25} - sys_days{2026y / November / 3};
    std::cout << "days until 2026-12-25: " << days_left.count() << '\n';

    sys_seconds stamp = sys_days{2026y / November / 3} + 9h + 30min;
    std::cout << std::format("UTC stamp: {:%Y-%m-%d %H:%M}\n", stamp);
}
''', "_tz": {"maybe_unsupported": True, "code": r'''
#include <chrono>
#include <format>
#include <iostream>

int main() {
    using namespace std::chrono;
    sys_seconds stamp = sys_days{2026y / November / 3} + 9h + 30min;   // 09:30 UTC
    zoned_time india{"Asia/Kolkata", stamp};
    zoned_time ny{"America/New_York", stamp};
    std::cout << std::format("India:    {:%Y-%m-%d %H:%M %Z}\n", india);
    std::cout << std::format("New York: {:%Y-%m-%d %H:%M %Z}\n", ny);
}
'''}},
takeaways=["Durations encode units; lossy conversions require `duration_cast`, `floor`, `ceil` or `round`.",
"Use `steady_clock` for intervals, `system_clock` for timestamps.",
"C++20 calendar types make invalid dates explicit; you choose how to normalize.",
"Store UTC; convert with `zoned_time` only for display (needs tzdb support)."],
quiz=[("Why does `std::chrono::seconds s = 1500ms;` not compile?", "The conversion would lose information (truncate), so it must be explicit."),
("Which clock should measure how long a function takes?", "`std::chrono::steady_clock` — it's monotonic and unaffected by wall-clock adjustments."),
("What is `2026y/January/31 + months{1}`?", "`2026-02-31`, an invalid `year_month_day` (`ok()` is false) that you must clamp or normalize.")]),

dict(title="A tour of the rest: random, regex, math, bits, limits, and more", std="C++23", minutes=12, area="Standard library: utilities",
features=[("`<random>`: engines, distributions, seeding", "C++11"), ("`<regex>`", "C++11"), ("`<cmath>` special functions, `<numbers>` constants", "C++17/20"), ("`std::numeric_limits`", "C++98"), ("`std::bitset`", "C++98"), ("`std::source_location`", "C++20"), ("`std::stacktrace`", "C++23"), ("`<locale>` basics", "C++98"), ("`std::hash`", "C++11"), ("`<cstdint>` fixed-width types (recap)", "C++11")],
why="""
The standard library has many smaller headers that each solve one problem well — and a couple that are
famously slow or awkward. This lesson is a guided tour: what each is for, the idiomatic call, and the one
pitfall to remember.
""",
body="""
## `<random>`: never `rand()`

```cpp
std::mt19937 rng{std::random_device{}()};          // engine, seeded
std::uniform_int_distribution<int> die{1, 6};      // distribution
int roll = die(rng);
```

`rand() % 6` is biased and low quality. Engines are deterministic given a seed (great for reproducible
tests); distributions shape the output. Note: *distributions* are not guaranteed to produce identical
sequences across standard library implementations — only engines are.

## `<regex>`: correct but slow

`std::regex` works, but common implementations are slow and can blow the stack on long inputs. Fine for
config parsing; for hot paths use a dedicated library (RE2, PCRE2, CTRE) or hand-written parsing.

## Math, constants and limits

`<numbers>` (C++20) gives `std::numbers::pi`, `e`, `sqrt2`... `<cmath>` has `std::hypot`, `std::lerp`
(C++20), special functions (`std::beta`, `std::cyl_bessel_j`). `std::numeric_limits<T>` tells you `max()`,
`lowest()`, `epsilon()`, `infinity()`. Remember: `numeric_limits<float>::min()` is the smallest *positive*
normal value, not the most negative!

## Debugging helpers

`std::source_location::current()` (C++20) gives file, line and function — a macro-free logging helper.
`std::stacktrace` (C++23) captures a call stack (library support varies; GCC needs `-lstdc++exp`), so it's
mentioned but not compiled here.

{{ex}}

## `std::bitset` and `<locale>`

`std::bitset<N>` is a fixed-size bit array with `count()`, `test()`, and string conversion — handy for flags
and register maps. `<locale>` controls number formatting, character classification and collation; it's
global, stateful and slow, which is why `std::format` and `from_chars` are locale-independent by default.
""",
files={"": r'''
#include <bitset>
#include <cmath>
#include <iostream>
#include <limits>
#include <numbers>
#include <random>
#include <regex>
#include <source_location>
#include <string>
#include <string_view>

void log(std::string_view msg, std::source_location loc = std::source_location::current()) {
    std::cout << "[" << loc.function_name() << ":" << loc.line() << "] " << msg << '\n';
}

int main() {
    std::mt19937 rng{12345};                                   // fixed seed: reproducible engine
    std::mt19937 rng2{12345};
    std::cout << std::boolalpha << "same seed, same first value: " << (rng() == rng2()) << '\n';
    std::uniform_int_distribution<int> die{1, 6};
    int counts[7]{};
    for (int i = 0; i < 6000; ++i) ++counts[die(rng)];
    bool roughly_uniform = true;
    for (int f = 1; f <= 6; ++f) roughly_uniform = roughly_uniform && counts[f] > 850 && counts[f] < 1150;
    std::cout << "6000 rolls roughly uniform: " << roughly_uniform << '\n';

    std::regex tag{R"((\w+)=(\d+))"};
    std::string cfg = "rate=48000 bits=24 ch=2";
    for (std::sregex_iterator it{cfg.begin(), cfg.end(), tag}, end; it != end; ++it)
        std::cout << (*it)[1] << " -> " << (*it)[2] << "; ";
    std::cout << '\n';

    std::cout << "pi=" << std::numbers::pi << " hypot(3,4)=" << std::hypot(3.0, 4.0)
              << " lerp(0,10,0.25)=" << std::lerp(0.0, 10.0, 0.25) << '\n';
    std::cout << "int max=" << std::numeric_limits<int>::max()
              << " float min (smallest positive normal)=" << std::numeric_limits<float>::min()
              << " float lowest=" << std::numeric_limits<float>::lowest() << '\n';
    std::cout << "0.1+0.2==0.3? " << (0.1 + 0.2 == 0.3)
              << ", within epsilon? " << (std::abs(0.1 + 0.2 - 0.3) < std::numeric_limits<double>::epsilon()) << '\n';

    std::bitset<8> status{"10010110"};
    status.set(0);
    std::cout << "status=" << status << " count=" << status.count() << " bit7=" << status.test(7) << '\n';

    log("hello from source_location");
}
''', "std": "c++23"},
takeaways=["Use `<random>` engines + distributions; never `rand() % n`.",
"`std::regex` is correct but slow; avoid it in hot paths.",
"`<numbers>`, `<cmath>` and `numeric_limits` cover constants, math and type limits (`min()` is positive for floats!).",
"`source_location` replaces `__FILE__`/`__LINE__` macros; `bitset` handles flags."],
quiz=[("Why is `rand() % 6` a poor die?", "`rand()` is low-quality and `%` introduces bias when RAND_MAX+1 isn't a multiple of 6; use `std::uniform_int_distribution` with a good engine."),
("What is `std::numeric_limits<float>::min()`?", "The smallest positive normalized float (~1.18e-38), not the most negative value — that's `lowest()`."),
("Are `std::uniform_int_distribution` results identical across GCC and Clang for the same seed?", "Not guaranteed — engines are specified exactly, but distribution algorithms are implementation-specific.")]),
],
assignment=dict(std="c++23", title="A media library scanner", task="""
Write a tool that scans a directory tree for audio files (`.wav`, `.flac`, `.mp3`), and prints a report:
count per extension, total size, and the 3 largest files — formatted as an aligned table with `std::println`.

Create a test directory under `fs::temp_directory_path()` with a few files of known sizes, run the scan, then
remove it. Use `error_code` overloads for cleanup, and sort results for deterministic output.
""", solution=r'''
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <map>
#include <print>
#include <ranges>
#include <string>
#include <system_error>
#include <vector>

namespace fs = std::filesystem;

struct FileInfo { std::string rel; std::uintmax_t size; };

int main() {
    const fs::path root = fs::temp_directory_path() / "cpp_course_scan";
    std::error_code ec;
    fs::remove_all(root, ec);
    fs::create_directories(root / "album1");
    fs::create_directories(root / "album2");
    struct Make { const char* name; std::size_t size; };
    for (auto [name, size] : {Make{"album1/a.wav", 4000}, Make{"album1/b.flac", 2500}, Make{"album2/c.mp3", 900},
                              Make{"album2/d.wav", 6000}, Make{"album2/notes.txt", 100}}) {
        std::ofstream{root / name, std::ios::binary} << std::string(size, 'x');
    }

    std::map<std::string, int> per_ext;
    std::vector<FileInfo> files;
    std::uintmax_t total = 0;
    for (const auto& e : fs::recursive_directory_iterator(root, ec)) {
        if (!e.is_regular_file()) continue;
        auto ext = e.path().extension().string();
        if (ext != ".wav" && ext != ".flac" && ext != ".mp3") continue;
        ++per_ext[ext];
        files.push_back({fs::relative(e.path(), root).generic_string(), e.file_size()});
        total += e.file_size();
    }
    std::ranges::sort(files, [](const FileInfo& a, const FileInfo& b) { return a.size != b.size ? a.size > b.size : a.rel < b.rel; });

    std::println("{:<8}{:>6}", "ext", "count");
    for (const auto& [ext, n] : per_ext) std::println("{:<8}{:>6}", ext, n);
    std::println("total: {} files, {} bytes", files.size(), total);
    std::println("largest:");
    for (const auto& f : files | std::views::take(3)) std::println("  {:<16}{:>8}", f.rel, f.size);

    fs::remove_all(root, ec);
    std::println("cleanup ok: {}", !ec);
}
'''))
