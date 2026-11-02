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
