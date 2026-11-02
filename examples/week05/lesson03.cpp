#include <cstring>
#include <iostream>
#include <utility>
#include <vector>

struct Counts { int copies = 0, moves = 0; } counts;

class Frame {
public:
    explicit Frame(std::size_t n) : n_{n}, px_{new unsigned char[n]{}} {}
    ~Frame() { delete[] px_; }
    Frame(const Frame& o) : n_{o.n_}, px_{new unsigned char[o.n_]} {
        std::memcpy(px_, o.px_, n_);
        ++counts.copies;
    }
    Frame(Frame&& o) noexcept : n_{std::exchange(o.n_, 0)}, px_{std::exchange(o.px_, nullptr)} {
        ++counts.moves;                          // steal; leave o empty but valid
    }
    Frame& operator=(Frame o) noexcept {         // handles both copy and move assignment
        std::swap(n_, o.n_);
        std::swap(px_, o.px_);
        return *this;
    }
    std::size_t size() const { return n_; }
private:
    std::size_t n_;
    unsigned char* px_;
};

struct NoexceptLess {               // move constructor NOT noexcept
    NoexceptLess() = default;
    NoexceptLess(const NoexceptLess&) { ++counts.copies; }
    NoexceptLess(NoexceptLess&&) { ++counts.moves; }
};

int main() {
    Frame a{3840 * 2160 * 4};
    Frame b = a;                 // copy: allocates and memcpy's ~33 MB
    Frame c = std::move(a);      // move: steals the pointer
    std::cout << "copies=" << counts.copies << " moves=" << counts.moves
              << " a.size()=" << a.size() << " c.size()=" << c.size() << '\n';

    counts = {};
    std::vector<Frame> v;
    for (int i = 0; i < 5; ++i) v.push_back(Frame{16});   // growth moves (noexcept)
    std::cout << "vector<Frame>: copies=" << counts.copies << " moves=" << counts.moves << '\n';

    counts = {};
    std::vector<NoexceptLess> w;
    for (int i = 0; i < 5; ++i) w.emplace_back();          // growth must COPY existing elements
    std::cout << "vector<NoexceptLess>: copies=" << counts.copies << " moves=" << counts.moves << '\n';

    const Frame k{8};
    Frame m = std::move(k);      // const: this silently copies!
    std::cout << "after moving a const: copies=" << counts.copies + 0 << " (one more copy)\n";
    (void)m;
}
