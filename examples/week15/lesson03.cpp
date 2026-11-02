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
