WEEK = dict(num=10, title="The standard library I: containers and iterators", intro="""
Choosing the right container is one of the highest-leverage decisions in C++ — often worth more than any
micro-optimization. This week tours every standard container, explains its complexity and memory layout,
and gives you a decision procedure. The short version, which we'll justify with measurements:
**default to `std::vector`.**
""", lessons=[
dict(title="std::vector in depth", std="C++20", minutes=12, area="Standard library: containers",
features=[("`std::vector`: size vs capacity, growth, `reserve`, `shrink_to_fit`", "C++98"), ("`emplace_back` vs `push_back`", "C++11"), ("Iterator invalidation rules", "C++98"), ("`std::erase` / `std::erase_if` (uniform erasure)", "C++20"), ("Erase-remove idiom", "C++98"), ("`std::vector<bool>` specialization", "C++98"), ("`append_range`, `insert_range`", "C++23")],
why="""
`std::vector` is a contiguous, growable array — and contiguous memory is what modern CPUs love: caches
prefetch it, SIMD chews through it. Even for operations where a linked list "should" win on paper,
`vector` often wins in practice. Let's understand it deeply: growth, invalidation, and the idioms that
keep it fast.
""",
body="""
## Size, capacity and growth

A vector owns a heap buffer with `capacity()` slots, of which `size()` are in use. When you `push_back`
into a full vector, it allocates a bigger buffer (typically 1.5× or 2×), moves the elements over, and frees
the old one. Growth is geometric, so `push_back` is **amortized O(1)**. If you know the final size,
`reserve(n)` avoids all the reallocations.

{{ex}}

## Iterator invalidation: the classic bug

```cpp
for (auto it = v.begin(); it != v.end(); ++it)
    if (*it == 0) v.push_back(1);     // WRONG: push_back may reallocate -> `it` dangles (UB)
```

Rules for vector: a reallocation invalidates **all** iterators, pointers and references; `insert`/`erase`
without reallocation invalidate those **at or after** the point. Holding `&v[0]` across a `push_back` is the
same bug. Prefer indices when you must modify while iterating, or collect changes and apply them after.

## Erasing elements

C++20's `std::erase_if(v, pred)` does it in one line. Before C++20 you'd use the *erase-remove idiom*:
`v.erase(std::remove_if(v.begin(), v.end(), pred), v.end());` — `remove_if` only shuffles the kept elements
forward; `erase` chops off the tail.

## `emplace_back` vs `push_back`

`emplace_back(args...)` constructs the element in place from constructor arguments; `push_back(obj)` copies or
moves an existing object. For an already-built object they're the same. Note `emplace_back` can call
`explicit` constructors, which can hide mistakes — prefer `push_back` unless you're constructing in place.

!!! warning "`std::vector<bool>` is not a container of bools"
    It packs bits, so `v[i]` returns a proxy object, not `bool&`; `auto& b = v[0];` doesn't compile and
    `&v[0]` isn't a `bool*`. Use `std::vector<char>`, `std::bitset` or `std::vector<std::uint8_t>` when you
    need real elements.
""",
files={"": r'''
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

struct Sample { int t; float v; Sample(int tt, float vv) : t{tt}, v{vv} {} };

int main() {
    std::vector<int> v;
    std::size_t last_cap = v.capacity();
    int reallocs = 0;
    for (int i = 0; i < 1000; ++i) {
        v.push_back(i);
        if (v.capacity() != last_cap) { ++reallocs; last_cap = v.capacity(); }
    }
    std::cout << "size=" << v.size() << " reallocations=" << reallocs << " (geometric growth; count is implementation-specific)\n";

    std::vector<int> r;
    r.reserve(1000);
    const int* before = r.data();
    for (int i = 0; i < 1000; ++i) r.push_back(i);
    std::cout << "with reserve: buffer moved? " << std::boolalpha << (before != r.data()) << '\n';

    std::vector<Sample> samples;
    samples.emplace_back(0, 0.5f);                   // constructed in place
    samples.push_back(Sample{1, 0.25f});
    std::cout << "samples=" << samples.size() << '\n';

    std::vector<int> data{5, 0, 3, 0, 0, 7, 1};
    std::vector<int> copy = data;
    auto removed = std::erase_if(data, [](int x) { return x == 0; });             // C++20
    copy.erase(std::remove(copy.begin(), copy.end(), 0), copy.end());              // classic idiom
    std::cout << "removed " << removed << ": ";
    for (int x : data) std::cout << x << ' ';
    std::cout << "| idiom gives same? " << (data == copy) << '\n';

    std::vector<int> work{1, 0, 2};                  // safe modification while iterating: indices
    for (std::size_t i = 0; i < work.size(); ++i)
        if (work[i] == 0) work.push_back(9);
    std::cout << "work.size()=" << work.size() << '\n';

    std::vector<bool> flags(10);
    flags[3] = true;
    auto proxy = flags[3];                            // a proxy, not bool&
    std::cout << "vector<bool> proxy reads " << static_cast<bool>(proxy) << '\n';
}
''', "compare": False},
takeaways=["`vector` is contiguous and cache-friendly; growth is geometric so `push_back` is amortized O(1).",
"`reserve` when you know the size; reallocation invalidates all iterators, pointers and references.",
"Use `std::erase_if` (C++20) or erase-remove to delete elements.",
"`std::vector<bool>` is a bit-packed special case with proxy references."],
quiz=[("Why is `push_back` amortized O(1) even though reallocation is O(n)?", "Capacity grows geometrically, so the total copying cost over n insertions is O(n) — O(1) per insertion on average."),
("After `v.push_back(x)` causes a reallocation, which iterators are valid?", "None of the old ones: all iterators, pointers and references into the vector are invalidated."),
("What does `std::remove` actually do?", "It moves the kept elements to the front and returns the new logical end; it doesn't change the size — you must `erase` the tail.")]),

dict(title="array, deque, list, and forward_list", std="C++20", minutes=10, area="Standard library: containers",
features=[("`std::array`, `std::to_array`", "C++11/20"), ("`std::deque`", "C++98"), ("`std::list`, `splice`", "C++98"), ("`std::forward_list`", "C++11"), ("Complexity guarantees and cache effects", "—")],
why="""
`std::vector` is the default, but not the only answer. A fixed-size table of filter coefficients doesn't
need the heap at all (`std::array`). A queue that grows at both ends wants `std::deque`. And sometimes you
genuinely need stable element addresses or O(1) splicing (`std::list`). Let's see when each one earns its
place — and measure why lists usually don't.
""",
body="""
| Container | Layout | Fast operations | Iterators stable? |
|---|---|---|---|
| `array<T,N>` | inline, fixed | everything; no heap | yes (never reallocates) |
| `vector<T>` | contiguous heap block | back insert/erase, random access | until reallocation |
| `deque<T>` | blocks of elements | front *and* back insert, random access | references stable for end inserts; iterators not |
| `list<T>` | doubly linked nodes | insert/erase anywhere given an iterator, `splice` | yes |
| `forward_list<T>` | singly linked nodes | same, less memory, forward only | yes |

## Big-O isn't everything

Inserting in the middle of a `list` is O(1) — *once you have the iterator*. Finding the position is O(n)
pointer chasing, with a likely cache miss per node. A `vector` insert is O(n) but it's a `memmove` of
contiguous memory, which modern CPUs do extremely fast. The example times both (timings are printed for
you to look at on your machine; they vary).

{{ex}}

## When `list` really wins

- You need iterators/pointers to elements to stay valid while others are inserted/erased (e.g. an LRU
  cache: `list` + `unordered_map` of iterators).
- You move ranges between lists with `splice` in O(1) without copying elements.
- Elements are huge and non-movable.

`std::to_array` (C++20) creates a `std::array` with the size deduced: `auto a = std::to_array({1, 2, 3});`.
""",
files={"": {"compare": False, "code": r'''
#include <array>
#include <chrono>
#include <deque>
#include <forward_list>
#include <iostream>
#include <list>
#include <vector>

template <typename C>
long long insert_middle_ms(int n) {
    C c;
    auto t0 = std::chrono::steady_clock::now();
    for (int i = 0; i < n; ++i) {
        auto it = c.begin();
        std::advance(it, static_cast<long>(c.size() / 2));   // find the middle: O(n) either way
        c.insert(it, i);
    }
    auto t1 = std::chrono::steady_clock::now();
    return std::chrono::duration_cast<std::chrono::milliseconds>(t1 - t0).count();
}

int main() {
    constexpr auto coeffs = std::to_array({0.25f, 0.5f, 0.25f});   // no heap, size deduced
    static_assert(coeffs.size() == 3);

    std::deque<int> dq{2, 3};
    dq.push_front(1);
    dq.push_back(4);
    std::cout << "deque: " << dq.front() << ".." << dq.back() << " [2]=" << dq[2] << '\n';

    std::list<int> a{1, 2, 3}, b{10, 20};
    auto keep = a.begin();                                  // iterator to 1
    a.splice(std::next(a.begin()), b);                      // O(1): moves nodes, no copies
    std::cout << "list after splice: ";
    for (int x : a) std::cout << x << ' ';
    std::cout << "| b.size()=" << b.size() << " | iterator still valid: " << *keep << '\n';

    std::forward_list<int> fl{3, 2, 1};
    fl.push_front(4);
    fl.sort();
    std::cout << "forward_list sorted front: " << fl.front() << '\n';

    const int n = 20000;
    std::cout << "insert " << n << " in the middle (your timings will differ):\n";
    std::cout << "  vector: " << insert_middle_ms<std::vector<int>>(n) << " ms\n";
    std::cout << "  list:   " << insert_middle_ms<std::list<int>>(n) << " ms\n";
}
'''}},
takeaways=["`std::array` for fixed sizes (no heap); `deque` for both-end queues; `vector` for almost everything else.",
"Linked lists have O(1) insertion given an iterator but terrible cache behaviour; finding the position dominates.",
"Choose `list` for stable iterators and O(1) `splice`, not for 'fast insertion'.",
"Measure on your hardware — complexity classes hide constant factors."],
quiz=[("Why is `vector` typically faster than `list` at 'insert in the middle' for ints?", "Finding the middle is O(n) for both, but vector's traversal and shift are contiguous memory operations that are cache- and prefetch-friendly, while the list chases pointers with cache misses."),
("What does `splice` do and why is it O(1)?", "It relinks nodes from one list into another without copying or allocating; only pointers change."),
("Does `std::array` allocate on the heap?", "No — its elements are stored inline in the object (on the stack for a local).")]),

dict(title="Associative and unordered containers", std="C++20", minutes=12, area="Standard library: containers",
features=[("`std::map`, `std::set`, `multimap`, `multiset`", "C++98"), ("`std::unordered_map`, `unordered_set` (+multi)", "C++11"), ("`try_emplace`, `insert_or_assign`", "C++17"), ("Node handles: `extract`, `merge`", "C++17"), ("`contains`", "C++20"), ("Heterogeneous lookup (transparent comparators/hashes)", "C++14/20"), ("Custom hash functions, `std::hash` specialization", "C++11")],
why="""
"Look up a sample by its name." "Count how many times each word appears." "Keep events sorted by time."
These are the jobs of associative containers. You have two families: tree-based (`map`, `set`), sorted with
O(log n) operations, and hash-based (`unordered_map`, `unordered_set`), unsorted with O(1) average. Knowing
their APIs well — `try_emplace`, `contains`, heterogeneous lookup — avoids a lot of slow, buggy code.
""",
body="""
## The `operator[]` trap

```cpp
std::map<std::string, int> counts;
if (counts["drums"] > 0) ...     // WRONG for a lookup: inserts "drums" -> 0 if missing!
```

`operator[]` inserts a default value when the key is missing (and so doesn't work on a `const` map). For
lookups use `find`, `contains` (C++20) or `at` (throws if missing).

## Insertion done right

- `try_emplace(key, args...)` — constructs the value only if the key is absent.
- `insert_or_assign(key, value)` — explicit upsert, tells you which happened.

## Heterogeneous lookup

With `std::map<std::string, int>`, `m.find("drums")` creates a temporary `std::string`. Use a *transparent*
comparator, `std::map<std::string, int, std::less<>>`, and lookups with `std::string_view` or `const char*`
allocate nothing. For unordered containers (C++20) you need a transparent hash *and* `std::equal_to<>`.

{{ex}}

## Custom keys

`map` needs `operator<` (or a comparator) — `<=>` from Week 4 provides it. `unordered_map` needs a hash:
specialize `std::hash<Key>` or pass a hasher type. Combine field hashes carefully (the example uses a
simple `boost::hash_combine`-style mix).

## Which one?

| Need | Use |
|---|---|
| Sorted iteration, range queries (`lower_bound`) | `map`/`set` |
| Fastest average lookup, no order needed | `unordered_map`/`unordered_set` |
| Small, mostly-read data | sorted `vector` or `flat_map` (next lesson) |

Node handles (`extract`/`merge`, C++17) move elements between maps — even change a key — without
reallocating.
""",
files={"": r'''
#include <cstddef>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <string_view>
#include <unordered_map>

struct NoteKey {
    int octave; char name;
    bool operator==(const NoteKey&) const = default;
    auto operator<=>(const NoteKey&) const = default;
};
template <> struct std::hash<NoteKey> {
    std::size_t operator()(const NoteKey& k) const noexcept {
        std::size_t h = std::hash<int>{}(k.octave);
        h ^= std::hash<char>{}(k.name) + 0x9e3779b9 + (h << 6) + (h >> 2);   // hash_combine
        return h;
    }
};

struct StringHash {                                       // transparent hash (C++20 lookup)
    using is_transparent = void;
    std::size_t operator()(std::string_view s) const { return std::hash<std::string_view>{}(s); }
};

int main() {
    std::map<std::string, int, std::less<>> counts;       // transparent comparator
    for (std::string_view w : {"kick", "snare", "kick", "hat", "kick"}) ++counts[std::string{w}];
    for (const auto& [word, n] : counts) std::cout << word << '=' << n << ' ';   // sorted
    std::cout << '\n';

    std::cout << std::boolalpha << "contains(\"tom\") " << counts.contains("tom")
              << ", size still " << counts.size() << '\n';
    (void)counts["tom"];                                   // the trap: inserts!
    std::cout << "after operator[]: size " << counts.size() << '\n';

    auto [it, inserted] = counts.try_emplace("kick", 100);
    std::cout << "try_emplace kick inserted? " << inserted << " value " << it->second << '\n';
    auto [it2, ins2] = counts.insert_or_assign("hat", 9);
    std::cout << "insert_or_assign hat inserted? " << ins2 << " value " << it2->second << '\n';

    auto lo = counts.lower_bound("j"), hi = counts.upper_bound("s");     // range query
    std::cout << "keys in [j, s]: ";
    for (auto i = lo; i != hi; ++i) std::cout << i->first << ' ';
    std::cout << '\n';

    std::unordered_map<std::string, int, StringHash, std::equal_to<>> bpm{{"techno", 130}, {"house", 124}};
    std::string_view genre = "house";
    if (auto f = bpm.find(genre); f != bpm.end()) std::cout << genre << " -> " << f->second << '\n';   // no temp string

    std::unordered_map<NoteKey, double> freq{{{4, 'A'}, 440.0}, {{5, 'A'}, 880.0}};
    std::cout << "A4=" << freq.at({4, 'A'}) << '\n';

    std::set<int> s1{1, 3, 5}, s2{2, 3, 4};
    s1.merge(s2);                                          // moves nodes; duplicates stay in s2
    std::cout << "merged size " << s1.size() << ", left in s2: " << *s2.begin() << '\n';
    auto node = s1.extract(5);
    node.value() = 50;                                     // change a key without reallocating
    s1.insert(std::move(node));
    std::cout << "largest now " << *s1.rbegin() << '\n';
}
'''},
takeaways=["`operator[]` inserts on a miss; use `find`, `contains` or `at` for lookups.",
"Use `try_emplace` and `insert_or_assign` for clear insertion semantics.",
"Transparent comparators/hashes enable lookups by `string_view` without temporaries.",
"Tree containers are ordered (range queries); hash containers are faster on average but unordered."],
quiz=[("Why doesn't `counts[\"x\"]` compile on a `const std::map`?", "`operator[]` may insert, so it's non-const; use `at` or `find`."),
("What do you need for heterogeneous lookup in `std::unordered_map` (C++20)?", "A transparent hash (with `is_transparent`) and a transparent equality such as `std::equal_to<>`."),
("What's the advantage of `extract` + `insert` over erase + insert?", "The node is reused — no deallocation/allocation and no copy of the value — and you can even modify the key.")]),

dict(title="Container adaptors, flat_map and flat_set", std="C++23", minutes=10, area="Standard library: containers",
features=[("`std::stack`, `std::queue`", "C++98"), ("`std::priority_queue`", "C++98"), ("`std::flat_map`, `std::flat_set` (+multi)", "C++23"), ("Sorted vector as a set/map", "—")],
why="""
A task scheduler needs "give me the highest-priority job". An undo system needs "last in, first out". These
aren't new data structures — they're *interfaces* on top of existing containers, called adaptors. And
C++23 adds `flat_map`, a map that stores its data in sorted vectors, because for many workloads that beats a
tree by a wide margin.
""",
body="""
## Adaptors

| Adaptor | Default underlying container | Operations |
|---|---|---|
| `stack<T>` | `deque<T>` | `push`, `pop`, `top` |
| `queue<T>` | `deque<T>` | `push`, `pop`, `front`, `back` |
| `priority_queue<T>` | `vector<T>` (binary heap) | `push`, `pop`, `top` = largest |

`pop()` returns `void` — read `top()` first. (That's for exception safety: returning the popped element
by value could throw after it's been removed.) For a min-heap pass `std::greater<>` as comparator.

{{ex}}

## `flat_map` and `flat_set` (C++23)

They keep keys (and values) in sorted contiguous containers and binary-search them. Compared with `std::map`:

- Lookups and iteration: faster (cache-friendly, no pointer chasing).
- Insertions/erasures in the middle: O(n) (elements shift).
- Iterators invalidated by insertions (unlike `map`).

Great for data that's built once and read many times — configs, lookup tables, small maps. Compiler status:
libc++ ships them; GCC's libstdc++ added `<flat_map>` in GCC 15. The second example is therefore marked
"may be unsupported" in our checker. Before C++23, a sorted `std::vector` + `std::lower_bound` gives you the
same thing by hand.

{{ex:_flat}}
""",
files={"": r'''
#include <functional>
#include <iostream>
#include <queue>
#include <stack>
#include <string>
#include <vector>

struct Job {
    int priority; std::string name;
    bool operator<(const Job& o) const { return priority < o.priority; }
};

int main() {
    std::stack<std::string> undo;
    for (auto op : {"add track", "trim", "fade"}) undo.push(op);
    std::cout << "undo: " << undo.top() << '\n';
    undo.pop();
    std::cout << "then: " << undo.top() << '\n';

    std::queue<int> packets;
    for (int i = 1; i <= 3; ++i) packets.push(i);
    std::cout << "first packet: " << packets.front() << ", last: " << packets.back() << '\n';

    std::priority_queue<Job> jobs;
    jobs.push({1, "thumbnail"});
    jobs.push({5, "encode audio"});
    jobs.push({3, "upload"});
    while (!jobs.empty()) { std::cout << jobs.top().priority << ':' << jobs.top().name << ' '; jobs.pop(); }
    std::cout << '\n';

    std::priority_queue<int, std::vector<int>, std::greater<>> min_heap;   // smallest first
    for (int t : {30, 10, 20}) min_heap.push(t);
    std::cout << "next timer fires at " << min_heap.top() << "ms\n";
}
''', "_flat": {"std": "c++23", "maybe_unsupported": True, "code": r'''
#include <flat_map>
#include <flat_set>
#include <iostream>
#include <string>

int main() {
    std::flat_map<std::string, int> rates{{"cd", 44100}, {"dvd", 48000}, {"hires", 96000}};
    rates["phone"] = 8000;
    for (const auto& [k, v] : rates) std::cout << k << '=' << v << ' ';   // sorted, contiguous
    std::cout << '\n';
    std::cout << "keys stored contiguously: " << rates.keys().size() << '\n';

    std::flat_set<int> ids{5, 1, 3, 1};
    std::cout << "unique sorted ids: ";
    for (int i : ids) std::cout << i << ' ';
    std::cout << '\n';
}
'''}},
takeaways=["`stack`, `queue` and `priority_queue` are adaptors over other containers.",
"`pop()` returns void; read `top()`/`front()` first.",
"`priority_queue` is a max-heap by default; use `std::greater<>` for a min-heap.",
"`flat_map`/`flat_set` (C++23) store sorted contiguous data: fast lookup, slower mid insertion."],
quiz=[("Why does `std::stack::pop()` return `void`?", "Returning the removed element by value could throw (during the copy) after the element was already removed, losing it; splitting `top()` and `pop()` keeps the strong guarantee."),
("How do you make a min-heap with `std::priority_queue`?", "`std::priority_queue<T, std::vector<T>, std::greater<>>`."),
("When is `flat_map` a worse choice than `map`?", "When you do frequent insertions/erasures in a large container (O(n) shifts), or need iterators/references stable across insertions.")]),

dict(title="Views over data: span, mdspan, string_view, and inplace_vector (preview)", std="C++23", minutes=11, area="Standard library: containers",
features=[("`std::span` (static and dynamic extent)", "C++20"), ("`std::mdspan`, extents, layouts", "C++23"), ("Multidimensional `operator[]`", "C++23"), ("`std::inplace_vector`", "C++26 (preview)"), ("Non-owning views and lifetime", "—")],
why="""
A function that processes audio shouldn't care whether the samples live in a `std::vector`, a
`std::array`, a C array from a driver, or memory-mapped file data. It needs "a pointer and a length". Views
give exactly that, safely typed. `std::span` does 1-D; C++23's `std::mdspan` does images, matrices and
multichannel audio; and C++26's `std::inplace_vector` gives a vector with fixed capacity and no heap —
ideal for embedded.
""",
body="""
## `std::span<T>` recap

From Week 3: a non-owning (pointer, size) view over contiguous data. `std::span<const float>` for read-only
parameters; fixed extent `std::span<float, 4>` encodes the size in the type. `subspan`, `first`, `last` slice
without copying.

## `std::mdspan` (C++23)

A view over contiguous memory interpreted as N dimensions:

```cpp
std::mdspan img(pixels.data(), height, width);   // 2-D view
img[y, x] = 255;                                  // C++23 multidimensional subscript
```

The *layout* policy decides how indices map to memory: `layout_right` (row-major, C style, default),
`layout_left` (column-major, Fortran/BLAS style), `layout_stride`. Extents can be static or dynamic.
Support: libc++ (Clang 17+) and libstdc++ (GCC 15+); older toolchains lack it, so the example is marked
"may be unsupported" in our checker.

{{ex}}

## Lifetime: views never own

```cpp
std::span<int> bad() { std::vector<int> v{1,2,3}; return v; }   // dangling view!
```

A view is only valid while the data it refers to is alive and not reallocated. Never return a view to a
local; be careful storing views in members.

## `std::inplace_vector<T, N>` (C++26 preview)

A vector with capacity fixed at compile time, elements stored inline — no allocation, ever. `push_back` past
capacity throws, and `try_push_back` returns null instead. It's perfect for embedded systems and for "small
lists" in hot code. No major standard library shipped it at the time of writing, so we don't compile an
example here; the Week 16 embedded lesson and the ring-buffer capstone build similar fixed-capacity
containers by hand.

```cpp
// C++26 (not compiled in this course yet)
std::inplace_vector<int, 8> v;
v.push_back(1);
if (!v.try_push_back(2)) { /* full */ }
```
""",
files={"": {"std": "c++23", "maybe_unsupported": True, "code": r'''
#include <cstddef>
#include <iostream>
#include <mdspan>
#include <span>
#include <vector>

float peak(std::span<const float> s) {
    float p = 0;
    for (float x : s) p = (x < 0 ? -x : x) > p ? (x < 0 ? -x : x) : p;
    return p;
}

int main() {
    std::vector<float> interleaved{0.1f, -0.9f, 0.4f, 0.2f, -0.3f, 0.8f};   // L R L R L R
    std::cout << "peak(all)=" << peak(interleaved) << " peak(first 2)=" << peak(std::span{interleaved}.first(2)) << '\n';

    // View the same memory as frames x channels
    std::mdspan audio(interleaved.data(), 3, 2);
    for (std::size_t ch = 0; ch < audio.extent(1); ++ch) {
        float p = 0;
        for (std::size_t f = 0; f < audio.extent(0); ++f) {
            float a = audio[f, ch] < 0 ? -audio[f, ch] : audio[f, ch];
            if (a > p) p = a;
        }
        std::cout << "channel " << ch << " peak " << p << '\n';
    }

    std::vector<int> pixels(4 * 3, 0);
    std::mdspan img(pixels.data(), 3, 4);           // 3 rows x 4 cols, row-major
    img[1, 2] = 255;
    std::cout << "pixel (1,2) is element " << (&img[1, 2] - pixels.data()) << " in memory\n";

    std::mdspan<int, std::extents<std::size_t, 3, 4>, std::layout_left> col_major(pixels.data());
    std::cout << "column-major (1,2) is element " << (&col_major[1, 2] - pixels.data()) << '\n';
}
'''}},
takeaways=["`std::span` is the standard 1-D view; prefer it for buffer parameters.",
"`std::mdspan` (C++23) views memory as N dimensions with pluggable layouts.",
"Views never own; returning a view to local data dangles.",
"`std::inplace_vector` (C++26) is a fixed-capacity, no-heap vector — shown as a preview."],
quiz=[("In a row-major 3×4 `mdspan`, which memory element is `[1, 2]`?", "Element 1*4 + 2 = 6."),
("What's wrong with `std::span<int> f() { std::vector<int> v{1}; return v; }`?", "The span refers to `v`'s buffer, which is destroyed when `f` returns — a dangling view."),
("What happens when you `push_back` into a full `std::inplace_vector`?", "It throws `std::bad_alloc`; `try_push_back` returns a null pointer instead.")]),

dict(title="Iterators and iterator categories", std="C++20", minutes=11, area="Standard library: iterators",
features=[("Iterator categories (input, output, forward, bidirectional, random access, contiguous)", "C++98/20"), ("C++20 iterator concepts", "C++20"), ("`std::begin/end/size/data/ssize`", "C++11/17/20"), ("Iterator adaptors: `reverse_iterator`, `back_inserter`, `move_iterator`, `istream_iterator`", "C++98/11"), ("`std::advance`, `next`, `prev`, `distance`", "C++98/11"), ("Writing a custom iterator", "C++20"), ("Sentinels", "C++20")],
why="""
Iterators are the glue of the standard library: algorithms don't know about containers, only about
iterators. If you make *your* data structure provide iterators, every algorithm — `sort`, `find`,
`accumulate`, range-for, ranges — works on it for free. This lesson shows the categories and builds an
iterator for a ring buffer, the core of our embedded capstone.
""",
body="""
## Categories

Each category adds capabilities; algorithms require the weakest category they need:

| Category | Adds | Example |
|---|---|---|
| input | read once, `++` | `istream_iterator` |
| forward | multi-pass | `forward_list` |
| bidirectional | `--` | `list`, `map` |
| random access | `+ n`, `[]`, `<` | `deque` |
| contiguous (C++20) | elements adjacent in memory | `vector`, `array`, `span` |

`std::sort` needs random access, which is why `std::list` has its own `sort()` member.

## Adaptors

- `std::back_inserter(v)` — an output iterator that calls `push_back`.
- `std::make_reverse_iterator`, `rbegin/rend`.
- `std::make_move_iterator` — moves instead of copies when used with algorithms.
- `std::istream_iterator<T>` — reads values from a stream.

## Writing your own

A C++20 iterator needs: `value_type`, `difference_type`, `operator*`, `operator++` (pre and post), and
`operator==`. Satisfying `std::forward_iterator` then gets you every forward algorithm. Use `static_assert`
with the concept to check.

{{ex}}

## Sentinels

In C++20 ranges, the end of a range can be a *different type* than the iterator — a sentinel. E.g. "until
the null terminator" doesn't need a precomputed end pointer. We'll use this in Week 11.
""",
files={"": r'''
#include <algorithm>
#include <array>
#include <cstddef>
#include <iostream>
#include <iterator>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>

template <typename T, std::size_t N>
class Ring {
public:
    void push(T v) { data_[(head_ + size_) % N] = v; if (size_ < N) ++size_; else head_ = (head_ + 1) % N; }

    class iterator {
    public:
        using value_type = T;
        using difference_type = std::ptrdiff_t;
        iterator() = default;
        iterator(const Ring* r, std::size_t i) : r_{r}, i_{i} {}
        const T& operator*() const { return r_->data_[(r_->head_ + i_) % N]; }
        iterator& operator++() { ++i_; return *this; }
        iterator operator++(int) { auto t = *this; ++i_; return t; }
        bool operator==(const iterator& o) const { return i_ == o.i_; }
    private:
        const Ring* r_ = nullptr;
        std::size_t i_ = 0;
    };
    iterator begin() const { return {this, 0}; }
    iterator end() const { return {this, size_}; }
private:
    std::array<T, N> data_{};
    std::size_t head_ = 0, size_ = 0;
};
static_assert(std::forward_iterator<Ring<int, 4>::iterator>);

int main() {
    Ring<int, 4> r;
    for (int i = 1; i <= 6; ++i) r.push(i);              // keeps the last 4
    for (int x : r) std::cout << x << ' ';
    std::cout << "| sum=" << std::accumulate(r.begin(), r.end(), 0)
              << " max=" << *std::max_element(r.begin(), r.end()) << '\n';

    std::vector<int> copy;
    std::copy(r.begin(), r.end(), std::back_inserter(copy));
    std::cout << "copied " << copy.size() << ", reversed: ";
    for (auto it = copy.rbegin(); it != copy.rend(); ++it) std::cout << *it << ' ';
    std::cout << '\n';

    std::istringstream in{"3 1 4 1 5"};
    std::vector<int> parsed{std::istream_iterator<int>{in}, std::istream_iterator<int>{}};
    std::cout << "parsed " << parsed.size() << " ints, distance(begin,end)=" << std::distance(parsed.begin(), parsed.end()) << '\n';

    std::vector<std::string> src{"a", "b"}, dst;
    std::copy(std::make_move_iterator(src.begin()), std::make_move_iterator(src.end()), std::back_inserter(dst));
    std::cout << "moved: " << dst[0] << dst[1] << ", ssize=" << std::ssize(dst) << '\n';
    auto it = std::next(parsed.begin(), 2);
    std::cout << "third element: " << *it << ", prev: " << *std::prev(it) << '\n';
}
'''},
takeaways=["Algorithms work on iterators; the category determines which algorithms apply.",
"Iterator adaptors (`back_inserter`, reverse, move, stream) connect containers, streams and algorithms.",
"A custom iterator with a few members unlocks the whole algorithm library; check with C++20 concepts.",
"Sentinels let a range's end be a different type than its iterator."],
quiz=[("Why can't you call `std::sort` on a `std::list`?", "`std::sort` requires random-access iterators; list iterators are only bidirectional. Use `list::sort()`."),
("What does `std::back_inserter(v)` do when assigned to?", "Calls `v.push_back(value)`."),
("What minimum members does a C++20 forward iterator need?", "`value_type`, `difference_type`, `operator*`, pre- and post-increment, equality comparison, and default constructibility.")]),
],
assignment=dict(title="An LRU cache", task="""
Implement `LruCache<Key, Value>` with capacity N:

- `std::optional<Value> get(const Key&)` — returns the value and marks it most-recently used.
- `void put(Key, Value)` — inserts/updates; evicts the least-recently used entry when full.
- Both operations must be O(1) average: use `std::list` for recency order and `std::unordered_map` from key to
  list iterator (this is the classic case where `list`'s stable iterators and `splice` shine).
""", solution=r'''
#include <cstddef>
#include <iostream>
#include <list>
#include <optional>
#include <string>
#include <unordered_map>
#include <utility>

template <typename Key, typename Value>
class LruCache {
public:
    explicit LruCache(std::size_t cap) : cap_{cap} {}
    std::optional<Value> get(const Key& k) {
        auto it = index_.find(k);
        if (it == index_.end()) return std::nullopt;
        order_.splice(order_.begin(), order_, it->second);     // O(1) move to front
        return it->second->second;
    }
    void put(Key k, Value v) {
        if (auto it = index_.find(k); it != index_.end()) {
            it->second->second = std::move(v);
            order_.splice(order_.begin(), order_, it->second);
            return;
        }
        if (order_.size() == cap_) {
            std::cout << "  evict " << order_.back().first << '\n';
            index_.erase(order_.back().first);
            order_.pop_back();
        }
        order_.emplace_front(k, std::move(v));
        index_[std::move(k)] = order_.begin();
    }
private:
    std::size_t cap_;
    std::list<std::pair<Key, Value>> order_;
    std::unordered_map<Key, typename std::list<std::pair<Key, Value>>::iterator> index_;
};

int main() {
    LruCache<std::string, int> c{2};
    c.put("kick", 1);
    c.put("snare", 2);
    std::cout << "get kick: " << c.get("kick").value_or(-1) << '\n';
    c.put("hat", 3);                     // evicts snare (least recently used)
    std::cout << "get snare: " << c.get("snare").value_or(-1) << '\n';
    std::cout << "get hat: " << c.get("hat").value_or(-1) << '\n';
}
'''))
