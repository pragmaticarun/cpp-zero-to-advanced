WEEK = dict(num=11, title="The standard library II: algorithms and ranges", intro="""
"No raw loops" is a famous piece of C++ advice (from Sean Parent). It doesn't mean loops are evil; it means
that most loops are a well-known algorithm in disguise, and naming the algorithm makes code shorter,
clearer and often faster. This week covers the `<algorithm>` and `<numeric>` toolbox, then C++20 ranges,
which make algorithms composable.
""", lessons=[
dict(title="Algorithms I: searching, counting, sorting", std="C++20", minutes=12, area="Standard library: algorithms",
features=[("Non-modifying algorithms: `find`, `find_if`, `count_if`, `all_of/any_of/none_of`, `mismatch`, `search`", "C++98/11"), ("Sorting: `sort`, `stable_sort`, `partial_sort`, `nth_element`", "C++98"), ("Binary search: `lower_bound`, `upper_bound`, `equal_range`, `binary_search`", "C++98"), ("`min/max/minmax/clamp`, `min_element/max_element`", "C++98/11/17"), ("Strict weak ordering requirement", "C++98"), ("Range algorithms `std::ranges::*` with projections", "C++20")],
why="""
You have 10,000 recorded takes and want: the first one that's clipped, how many are longer than a minute,
the top 5 by loudness, and the median duration. Each of those is a one-liner with the right algorithm —
and each of the "obvious" hand-written loops has a subtle bug or a worse complexity. Let's learn the
toolbox.
""",
body="""
## Finding and counting

`find_if`, `count_if`, `any_of`/`all_of`/`none_of` replace most "search loops". In C++20, prefer the
`std::ranges::` versions: they take the container directly and support **projections** — a function applied
to each element before comparing:

```cpp
std::ranges::sort(takes, {}, &Take::loudness);   // sort by a member: no lambda needed
```

## Choosing a sort

| Need | Algorithm | Complexity |
|---|---|---|
| fully sorted | `sort` | O(n log n) |
| equal elements keep their order | `stable_sort` | O(n log n), may allocate |
| only the top k, sorted | `partial_sort` | O(n log k) |
| only the k-th element (e.g. median) | `nth_element` | O(n) average |

## The comparator rule

Comparators must be a **strict weak ordering**: `comp(a, a)` is false, and it's transitive. `<=` breaks the
rule — and with `std::sort` that's UB that can read out of bounds, not just "sort wrongly".

{{ex}}

## Binary search on sorted data

`lower_bound` returns the first element not less than the value; `upper_bound` the first greater;
`equal_range` both. They're O(log n) — *if* the range is sorted by the same comparison.
""",
files={"": r'''
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

struct Take { std::string name; int seconds; double loudness; bool clipped; };

int main() {
    std::vector<Take> takes{{"t1", 45, -14.0, false}, {"t2", 75, -9.5, true}, {"t3", 62, -11.0, false},
                            {"t4", 30, -20.0, false}, {"t5", 90, -8.0, true}, {"t6", 62, -12.5, false}};

    auto first_clip = std::ranges::find_if(takes, &Take::clipped);              // projection as predicate
    std::cout << "first clipped: " << first_clip->name << '\n';
    auto long_ones = std::ranges::count_if(takes, [](int s) { return s > 60; }, &Take::seconds);
    std::cout << "longer than 60s: " << long_ones << '\n';
    std::cout << std::boolalpha << "all under 2 min? "
              << std::ranges::all_of(takes, [](int s) { return s < 120; }, &Take::seconds) << '\n';

    auto by_loud = takes;
    std::ranges::partial_sort(by_loud, by_loud.begin() + 2, std::ranges::greater{}, &Take::loudness);
    std::cout << "top 2 loudest: " << by_loud[0].name << ' ' << by_loud[1].name << '\n';

    std::vector<int> durations;
    for (const auto& t : takes) durations.push_back(t.seconds);
    auto mid = durations.begin() + static_cast<long>(durations.size() / 2);
    std::ranges::nth_element(durations, mid);
    std::cout << "median-ish duration: " << *mid << '\n';

    auto stable = takes;
    std::ranges::stable_sort(stable, {}, &Take::seconds);                    // t3 stays before t6
    for (const auto& t : stable) std::cout << t.name << '(' << t.seconds << ") ";
    std::cout << '\n';

    std::ranges::sort(durations);
    auto [lo, hi] = std::ranges::equal_range(durations, 62);
    std::cout << "takes of exactly 62s: " << (hi - lo) << ", lower_bound(60) -> " << *std::ranges::lower_bound(durations, 60) << '\n';
    auto [mn, mx] = std::ranges::minmax(durations);
    std::cout << "min " << mn << " max " << mx << " clamp(200) " << std::clamp(200, mn, mx) << '\n';
}
'''},
takeaways=["Name your loops: `find_if`, `count_if`, `any_of`… say what they do.",
"Projections (`&Take::seconds`) let range algorithms work on a member without lambdas.",
"Pick the cheapest sort: `partial_sort` for top-k, `nth_element` for medians, `stable_sort` to keep order.",
"Comparators must be strict weak orderings; `<=` is UB with `std::sort`."],
quiz=[("What's the complexity of `nth_element`?", "O(n) on average."),
("Why is `[](int a, int b){ return a <= b; }` a broken comparator?", "It's not irreflexive (`comp(a, a)` is true), so it's not a strict weak ordering; `std::sort` may misbehave or read out of bounds."),
("What does `std::ranges::sort(v, {}, &T::x)` do?", "Sorts `v` by member `x` using the default comparator `std::ranges::less` on the projected values.")]),

dict(title="Algorithms II: transforming, removing, and numeric", std="C++23", minutes=11, area="Standard library: algorithms",
features=[("Modifying algorithms: `copy_if`, `transform`, `replace_if`, `fill`, `generate`, `rotate`, `reverse`, `unique`, `shuffle`", "C++98/11"), ("Set algorithms on sorted ranges: `set_union`, `set_intersection`, `includes`, `merge`", "C++98"), ("Heap algorithms: `make_heap`, `push_heap`, `pop_heap`", "C++98"), ("`<numeric>`: `accumulate`, `reduce`, `transform_reduce`, `inner_product`, `partial_sum`, `inclusive_scan`, `iota`, `gcd`, `lcm`, `midpoint`", "C++98/17/20"), ("`std::ranges::fold_left`", "C++23"), ("Output ranges and `back_inserter`", "C++98")],
why="""
Normalize a buffer, keep only the takes above a threshold, compute RMS loudness, build a running total —
these are transforms, filters and reductions. The standard library has them all, including parallel-ready
versions (`reduce`, `transform_reduce`) that we'll run on multiple cores in Week 14.
""",
body="""
## Transform, filter, replace

```cpp
std::ranges::transform(in, out.begin(), [](float x) { return x * gain; });
std::ranges::copy_if(takes, std::back_inserter(good), is_good);
```

Output algorithms *write through an iterator*; they never grow the destination. Writing into an empty
vector's `begin()` is UB — use `std::back_inserter` or size the destination first.

## Removing duplicates

`unique` removes *consecutive* duplicates (so sort first) and, like `remove`, returns the new end — then
`erase`.

## Numeric reductions

- `accumulate(first, last, init)` — left fold, strictly in order. **The init type decides the result type**:
  `accumulate(v.begin(), v.end(), 0)` on doubles sums into an `int`!
- `reduce` — like accumulate but may reorder (associative + commutative ops), enabling parallelism.
- `transform_reduce` — map then reduce: dot products, RMS.
- `partial_sum` / `inclusive_scan` / `exclusive_scan` — running totals.
- C++23 `std::ranges::fold_left` — the ranges-style accumulate.

{{ex}}

## Set and heap algorithms

On *sorted* ranges, `set_intersection`, `set_union`, `set_difference` and `includes` run in linear time.
Heap algorithms let you keep a heap inside your own vector — what `priority_queue` uses internally.

!!! tip "Pro tip: `std::midpoint`"
    `(a + b) / 2` can overflow; `std::midpoint(a, b)` (C++20) can't. It also handles pointers and floats
    correctly.
""",
files={"": r'''
#include <algorithm>
#include <cmath>
#include <iostream>
#include <iterator>
#include <numeric>
#include <random>
#include <string>
#include <vector>

int main() {
    std::vector<double> buf{0.5, -0.25, 0.75, -0.5};
    std::vector<double> loud(buf.size());
    std::ranges::transform(buf, loud.begin(), [](double x) { return x * 2.0; });

    std::vector<double> clipped;
    std::ranges::copy_if(loud, std::back_inserter(clipped), [](double x) { return std::abs(x) > 1.0; });
    std::cout << "samples over full scale after gain: " << clipped.size() << '\n';

    auto wrong = std::accumulate(buf.begin(), buf.end(), 0);       // int init: sums truncated values!
    auto right = std::accumulate(buf.begin(), buf.end(), 0.0);
    std::cout << "accumulate with 0: " << wrong << ", with 0.0: " << right << '\n';

    double rms = std::sqrt(std::transform_reduce(buf.begin(), buf.end(), buf.begin(), 0.0) / static_cast<double>(buf.size()));
    std::cout << "rms = " << rms << '\n';
    std::cout << "fold_left = " << std::ranges::fold_left(buf, 0.0, std::plus<>{}) << '\n';

    std::vector<int> frames{3, 1, 4, 1, 5};
    std::vector<int> offsets(frames.size());
    std::exclusive_scan(frames.begin(), frames.end(), offsets.begin(), 0);     // where each chunk starts
    for (int o : offsets) std::cout << o << ' ';
    std::cout << "(offsets)\n";

    std::vector<int> ids(6);
    std::iota(ids.begin(), ids.end(), 100);
    std::ranges::rotate(ids, ids.begin() + 2);
    std::ranges::reverse(ids);
    std::cout << "ids: ";
    for (int i : ids) std::cout << i << ' ';
    std::cout << '\n';

    std::vector<std::string> tags{"rock", "jazz", "rock", "funk", "jazz"};
    std::ranges::sort(tags);
    auto [first, last] = std::ranges::unique(tags);
    tags.erase(first, last);
    std::cout << "unique tags: " << tags.size() << '\n';

    std::vector<std::string> a{"funk", "jazz", "rock"}, b{"jazz", "pop"}, both;
    std::ranges::set_intersection(a, b, std::back_inserter(both));
    std::cout << "in both: " << both[0] << '\n';

    std::mt19937 rng{42};
    std::ranges::shuffle(ids, rng);                                 // deterministic for a given seed+library
    std::cout << "gcd(48000,44100)=" << std::gcd(48000, 44100) << " lcm=" << std::lcm(48000, 44100)
              << " midpoint(2e9,2.1e9)=" << std::midpoint(2'000'000'000, 2'100'000'000) << '\n';
}
''', "std": "c++23"},
takeaways=["Output algorithms write through iterators; use `back_inserter` or pre-size the destination.",
"`unique` and `remove` return a new end; erase the tail.",
"`accumulate`'s init value sets the result type — `0` vs `0.0` matters.",
"`reduce`/`transform_reduce` allow reordering (and parallelism); scans give running totals."],
quiz=[("What's wrong with `std::accumulate(v.begin(), v.end(), 0)` for `std::vector<double>`?", "The accumulator is `int`, so each partial sum is converted to int — the result is truncated."),
("Why must you sort before `std::unique` to remove all duplicates?", "`unique` only collapses consecutive equal elements."),
("How does `reduce` differ from `accumulate`?", "`reduce` may apply the operation in any order/grouping (requiring associativity and commutativity for deterministic results), which enables parallel execution; `accumulate` is strictly left-to-right.")]),

dict(title="Ranges and views", std="C++23", minutes=13, area="Standard library: ranges",
features=[("Ranges library, range concepts", "C++20"), ("Views: `filter`, `transform`, `take`, `drop`, `reverse`, `iota`, `split`, `join`, `keys/values/elements`", "C++20"), ("Pipe syntax `|`", "C++20"), ("Lazy evaluation", "C++20"), ("`std::ranges::to`", "C++23"), ("C++23 views: `zip`, `enumerate`, `chunk`, `slide`, `stride`, `cartesian_product`, `adjacent`, `join_with`", "C++23"), ("Dangling protection (`std::ranges::dangling`)", "C++20"), ("Borrowed ranges", "C++20")],
why="""
"Take the clipped takes, get their names, uppercase them, first three." With classic algorithms that's three
temporary vectors and a loop. With C++20 ranges it's one readable pipeline that runs lazily — no
temporaries, nothing computed until you iterate. This is the biggest change to everyday C++ style since
lambdas.
""",
body="""
## Views and pipes

A *view* is a lightweight, lazy range adaptor. Compose them with `|`:

```cpp
auto names = takes | std::views::filter(&Take::clipped)
                   | std::views::transform(&Take::name)
                   | std::views::take(3);
for (const auto& n : names) ...      // work happens here, element by element
```

C++23 adds `std::ranges::to<std::vector>()` to materialize a pipeline, plus many views: `zip`,
`enumerate`, `chunk`, `slide`, `stride`, `adjacent`, `cartesian_product`, `join_with`.

{{ex}}

## Laziness has consequences

1. **Views don't own** (except `owning_view`). A view over a temporary vector dangles; the library catches
   some cases by returning `std::ranges::dangling` from algorithms called on temporaries.
2. **Some views cache.** `filter_view::begin()` caches its result, so iterating a filter view while
   modifying the underlying elements that affect the predicate is a bug, and a `const` filter view isn't
   iterable.
3. **Re-iterating recomputes.** A `transform` over an expensive function runs it again each pass;
   materialize with `ranges::to` if you iterate many times.

## Generators of values

`std::views::iota(1, 11)` counts; `std::views::iota(1)` is infinite — combine with `take`. `std::views::istream<int>(in)`
reads from a stream lazily.

!!! tip "Pro tip: debugging"
    If a pipeline won't compile, build it up one adaptor at a time. Ranges errors are long, but the first
    "constraints not satisfied" line usually names the culprit view.
""",
files={"": r'''
#include <algorithm>
#include <cctype>
#include <iostream>
#include <map>
#include <ranges>
#include <string>
#include <string_view>
#include <vector>

struct Take { std::string name; int seconds; bool clipped; };

int main() {
    std::vector<Take> takes{{"intro", 30, false}, {"verse", 62, true}, {"chorus", 45, true},
                            {"bridge", 20, false}, {"outro", 75, true}, {"coda", 15, true}};

    auto upper = [](std::string s) { for (auto& c : s) c = static_cast<char>(std::toupper(static_cast<unsigned char>(c))); return s; };
    auto names = takes | std::views::filter(&Take::clipped)
                       | std::views::transform(&Take::name)
                       | std::views::transform(upper)
                       | std::views::take(3);
    for (const auto& n : names) std::cout << n << ' ';
    std::cout << '\n';

    auto squares = std::views::iota(1) | std::views::transform([](int i) { return i * i; })
                                       | std::views::take_while([](int x) { return x < 50; });
    auto v = squares | std::ranges::to<std::vector>();                  // C++23
    std::cout << "squares < 50: " << v.size() << " values, last " << v.back() << '\n';

    for (auto [i, t] : std::views::enumerate(takes) | std::views::take(2))   // C++23
        std::cout << i << ':' << t.name << ' ';
    std::cout << '\n';

    std::vector<int> left{1, 2, 3}, right{10, 20, 30};
    for (auto [l, r] : std::views::zip(left, right)) std::cout << l + r << ' ';
    std::cout << '\n';

    std::vector<int> samples{1, 2, 3, 4, 5, 6, 7};
    for (auto chunk : samples | std::views::chunk(3)) std::cout << '[' << std::ranges::fold_left(chunk, 0, std::plus<>{}) << ']';
    std::cout << " <- sums of chunks of 3\n";
    for (auto w : samples | std::views::slide(3)) std::cout << w[1] << ' ';
    std::cout << "<- centers of sliding windows\n";

    std::string_view csv = "kick,snare,hat";
    for (auto part : csv | std::views::split(',')) std::cout << std::string_view{part} << '|';
    std::cout << '\n';

    std::map<std::string, int> bpm{{"house", 124}, {"techno", 130}};
    for (const auto& k : bpm | std::views::keys) std::cout << k << ' ';
    for (int b : bpm | std::views::values | std::views::reverse) std::cout << b << ' ';
    std::cout << '\n';

    auto r = std::ranges::find(std::vector<int>{1, 2, 3}, 2);           // temporary: returns `dangling`
    static_assert(std::is_same_v<decltype(r), std::ranges::dangling>);
}
''', "std": "c++23", "maybe_unsupported": True},
takeaways=["Views are lazy, composable with `|`, and don't own their data.",
"C++23 adds `ranges::to`, `zip`, `enumerate`, `chunk`, `slide` and more.",
"Mind laziness: dangling views, caching in `filter`, recomputation on re-iteration.",
"Range algorithms on temporaries return `std::ranges::dangling` to prevent use-after-free."],
quiz=[("When does the work in `takes | views::filter(f) | views::transform(g)` happen?", "Lazily, element by element, as you iterate the resulting view — nothing is computed when the pipeline is built."),
("How do you turn a view into a `std::vector` in C++23?", "`view | std::ranges::to<std::vector>()`."),
("Why does `std::ranges::find(std::vector<int>{1,2,3}, 2)` return `std::ranges::dangling`?", "The argument is a temporary non-borrowed range; an iterator into it would dangle after the full expression, so the library returns a placeholder type that can't be dereferenced.")]),

dict(title="Utilities: pair, tuple, apply, function objects, and friends", std="C++23", minutes=10, area="Standard library: utilities",
features=[("`std::pair`, `std::tuple`, `std::tie`, `std::get`, `std::tuple_cat`", "C++98/11"), ("`std::apply`, `std::make_from_tuple`", "C++17"), ("Function objects: `std::plus<>`, `std::less<>`, `std::ranges::less`, `std::identity`", "C++98/14/20"), ("`std::not_fn`", "C++17"), ("`std::exchange`, `std::swap`, `std::as_const`, `std::to_underlying`", "C++14/17/23"), ("`std::integer_sequence` (recap)", "C++14"), ("`std::ref`/`std::cref`, `std::reference_wrapper`", "C++11")],
why="""
The `<utility>`, `<tuple>` and `<functional>` headers are full of small tools that remove boilerplate:
returning several values, calling a function with arguments stored in a tuple, flipping a predicate,
resetting a member while returning its old value. Individually tiny; together they make code noticeably
cleaner.
""",
body="""
## Pairs and tuples

`std::tuple<int, std::string, double>` groups values without naming a struct. Access with `std::get<0>(t)` or
`std::get<std::string>(t)` (if the type is unique) — or, better, structured bindings. Honest advice: if the
tuple escapes a small scope, a named `struct` with named fields is clearer.

`std::tie(a, b) = f();` assigns into existing variables; `std::tie(x.a, x.b) < std::tie(y.a, y.b)` was the
pre-`<=>` way to write lexicographic comparisons.

## `std::apply`

Calls a function with a tuple's elements as arguments — the bridge between stored arguments and calls (used
by thread pools and deferred tasks).

{{ex}}

## Function objects

`std::plus<>`, `std::less<>`, `std::greater<>` (the `<>` forms are transparent and generic). C++20 adds
`std::ranges::less` (concept-constrained) and `std::identity` (the default projection). `std::not_fn(pred)`
negates a predicate.

## Small helpers

- `std::exchange(x, new)` — set and return the old value: perfect for move constructors.
- `std::as_const(x)` — get a const reference (call const overloads).
- `std::to_underlying(e)` (C++23) — enum to its underlying integer.
- `std::ref(x)` — pass by reference through APIs that copy (like `std::thread` or `std::bind`).
""",
files={"": r'''
#include <algorithm>
#include <functional>
#include <iostream>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

std::tuple<int, std::string, double> parse_line() { return {7, "So What", 562.5}; }

struct Mixer {
    Mixer(int ch, std::string n) : channels{ch}, name{std::move(n)} {}
    int channels; std::string name;
};

enum class Codec : unsigned char { pcm = 1, opus = 2 };

void bump(int& x) { ++x; }

int main() {
    auto [id, title, secs] = parse_line();
    std::cout << id << ' ' << title << ' ' << secs << '\n';

    auto t = parse_line();
    std::cout << std::get<std::string>(t) << " / " << std::get<0>(t) << '\n';
    auto bigger = std::tuple_cat(t, std::make_tuple('x'));
    std::cout << "tuple_cat size: " << std::tuple_size_v<decltype(bigger)> << '\n';

    int a = 0; std::string b;
    std::tie(a, b, std::ignore) = parse_line();
    std::cout << "tie: " << a << ' ' << b << '\n';

    auto args = std::make_tuple(3, 4);
    std::cout << "apply: " << std::apply(std::plus<>{}, args) << '\n';
    auto m = std::make_from_tuple<Mixer>(std::make_tuple(2, std::string{"main"}));
    std::cout << "make_from_tuple: " << m.name << ' ' << m.channels << '\n';

    std::vector<int> v{5, 2, 8, 1};
    std::ranges::sort(v, std::greater<>{});
    auto is_even = [](int x) { return x % 2 == 0; };
    std::cout << "first odd: " << *std::ranges::find_if(v, std::not_fn(is_even)) << '\n';

    int counter = 10;
    int old = std::exchange(counter, 0);
    std::cout << "exchange: old " << old << " new " << counter << '\n';
    std::cout << "to_underlying(opus) = " << static_cast<int>(std::to_underlying(Codec::opus)) << '\n';

    int n = 1;
    auto f = std::bind_front(bump, std::ref(n));   // without std::ref, bump would modify a copy
    f(); f();
    std::cout << "n after ref binding: " << n << '\n';
}
''', "std": "c++23"},
takeaways=["Use tuples locally and structured bindings to unpack; prefer named structs for public APIs.",
"`std::apply` calls a function with a tuple's elements; `make_from_tuple` constructs an object.",
"Transparent function objects (`std::less<>`) and `std::not_fn` replace small lambdas.",
"`std::exchange`, `std::as_const`, `std::to_underlying` and `std::ref` remove common boilerplate."],
quiz=[("What does `std::exchange(x, 0)` return?", "The old value of `x`; `x` is set to 0."),
("Why is `std::ref(n)` needed in `std::bind_front(bump, std::ref(n))`?", "`bind_front` stores copies of its arguments; `std::ref` stores a reference wrapper so `bump` modifies the original `n`."),
("When does `std::get<std::string>(t)` fail to compile?", "When the tuple has zero or more than one element of type `std::string`.")]),

dict(title="Generators and lazy sequences with std::generator (C++23)", std="C++23", minutes=9, area="Standard library: ranges",
features=[("`std::generator`", "C++23"), ("`co_yield` in generators", "C++20"), ("Generators as ranges (compose with views)", "C++23"), ("Recursive generators (`elements_of`)", "C++23")],
why="""
Some sequences are easiest to describe as a loop that *produces* values one at a time: walk a directory tree,
read packets until EOF, generate an infinite stream of test tones. `std::generator` lets you write that loop
with `co_yield` and hand it out as a range that callers can pipe through views. It's a preview of
coroutines, which Week 14 explains properly.
""",
body="""
## Writing a generator

```cpp
std::generator<int> fibonacci() {
    int a = 0, b = 1;
    while (true) { co_yield a; a = std::exchange(b, a + b); }
}
for (int x : fibonacci() | std::views::take(10)) ...
```

The function body runs only as far as needed: each `co_yield` suspends it until the caller asks for the next
value. Infinite sequences are fine as long as the consumer stops.

{{ex}}

## Recursive generators

`co_yield std::ranges::elements_of(child_generator());` yields everything from a nested generator — handy for
tree traversals.

## Support status (honest)

`std::generator` is C++23 and is implemented in GCC 14's libstdc++, and in MSVC. libc++ (used by Clang on
macOS and by our local test compiler) did not ship it at the time of writing, so this example is marked
"may be unsupported": our CI compiles and runs it with GCC. If your toolchain lacks it, Week 14 shows how to
write a minimal generator yourself.

!!! warning "Lifetime pitfall"
    A generator that takes parameters *by reference* keeps referring to them while suspended. Passing a
    temporary (`gen(std::string{"x"})`) leaves a dangling reference after the first suspension. Take
    coroutine parameters by value.
""",
files={"": {"std": "c++23", "maybe_unsupported": True, "code": r'''
#include <generator>
#include <iostream>
#include <ranges>
#include <string>
#include <utility>
#include <vector>

std::generator<long long> fibonacci() {
    long long a = 0, b = 1;
    while (true) {
        co_yield a;
        a = std::exchange(b, a + b);
    }
}

std::generator<std::string> packets(std::vector<std::string> wire) {   // by value: no dangling
    for (auto& p : wire) {
        if (p == "EOF") co_return;
        co_yield "pkt:" + p;
    }
}

struct Node { std::string name; std::vector<Node> children; };

std::generator<const std::string&> walk(const Node& n) {
    co_yield n.name;
    for (const auto& c : n.children) co_yield std::ranges::elements_of(walk(c));
}

int main() {
    for (auto x : fibonacci() | std::views::drop(5) | std::views::take(5)) std::cout << x << ' ';
    std::cout << '\n';
    for (const auto& p : packets({"a", "b", "EOF", "c"})) std::cout << p << ' ';
    std::cout << '\n';
    Node root{"root", {{"drums", {{"kick", {}}, {"snare", {}}}}, {"bass", {}}}};
    for (const auto& name : walk(root)) std::cout << name << ' ';
    std::cout << '\n';
}
'''}},
takeaways=["`std::generator<T>` turns a `co_yield` loop into a lazy input range.",
"Generators compose with views; infinite generators are fine if the consumer stops.",
"`std::ranges::elements_of` yields from nested generators (recursion).",
"Take generator parameters by value; library support is still uneven (GCC 14+, MSVC)."],
quiz=[("What happens at `co_yield a;`?", "The generator produces `a` to the consumer and suspends; it resumes from that point when the consumer asks for the next value."),
("Why is `std::generator<int> g(const std::string& s)` risky?", "The coroutine may outlive the referenced argument (e.g. a temporary), leaving a dangling reference when resumed."),
("Is a generator a forward range?", "No — it's an input range: single-pass; you can iterate it only once.")]),
],
assignment=dict(std="c++23", title="A log analysis pipeline", task="""
Given lines like `"12:00:01 WARN disk 91%"`, write range pipelines (no raw `for` loops except for printing) to:

1. Count lines per level (`INFO`, `WARN`, `ERROR`) using `std::ranges::count_if`.
2. Collect the messages of the first 2 `ERROR` lines into a `std::vector<std::string>` with `std::ranges::to`.
3. Print the line numbers (1-based) of all `WARN` lines using `views::enumerate`.
""", solution={"maybe_unsupported": True, "code": r'''
#include <algorithm>
#include <iostream>
#include <ranges>
#include <string>
#include <string_view>
#include <vector>

std::string_view level(std::string_view line) {
    auto s = line.substr(line.find(' ') + 1);
    return s.substr(0, s.find(' '));
}
std::string_view message(std::string_view line) {
    auto s = line.substr(line.find(' ') + 1);
    return s.substr(s.find(' ') + 1);
}

int main() {
    std::vector<std::string_view> log{"12:00:01 INFO start", "12:00:02 WARN disk 91%", "12:00:03 ERROR write failed",
                                      "12:00:04 INFO retry", "12:00:05 ERROR write failed again", "12:00:06 WARN fan",
                                      "12:00:07 ERROR giving up"};
    for (std::string_view lv : {"INFO", "WARN", "ERROR"})
        std::cout << lv << ": " << std::ranges::count_if(log, [lv](auto l) { return level(l) == lv; }) << '\n';

    auto errors = log | std::views::filter([](auto l) { return level(l) == "ERROR"; })
                      | std::views::transform([](auto l) { return std::string{message(l)}; })
                      | std::views::take(2)
                      | std::ranges::to<std::vector>();
    for (const auto& e : errors) std::cout << "error: " << e << '\n';

    std::cout << "WARN on lines:";
    for (auto [i, l] : std::views::enumerate(log))
        if (level(l) == "WARN") std::cout << ' ' << i + 1;
    std::cout << '\n';
}
'''}))
