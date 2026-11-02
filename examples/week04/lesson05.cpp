#include <algorithm>
#include <compare>
#include <iostream>
#include <vector>

struct Version {
    int major = 0, minor = 0, patch = 0;
    auto operator<=>(const Version&) const = default;   // all six comparisons
    friend std::ostream& operator<<(std::ostream& os, const Version& v) {
        return os << v.major << '.' << v.minor << '.' << v.patch;
    }
};

struct Vec2 {
    double x = 0, y = 0;
    Vec2& operator+=(const Vec2& o) { x += o.x; y += o.y; return *this; }
    friend Vec2 operator+(Vec2 a, const Vec2& b) { return a += b; }   // a is a copy
    friend Vec2 operator*(double k, Vec2 v) { v.x *= k; v.y *= k; return v; }
    bool operator==(const Vec2&) const = default;
};

class Grid {
public:
    int& operator[](int r, int c) { return cells_[static_cast<std::size_t>(r * 3 + c)]; }   // C++23 multi-arg []
private:
    std::vector<int> cells_ = std::vector<int>(9);
};

int main() {
    std::vector<Version> vs{{2, 1, 0}, {1, 9, 9}, {2, 0, 5}, {2, 1, 0}};
    std::ranges::sort(vs);
    for (const auto& v : vs) std::cout << v << ' ';
    std::cout << '\n' << std::boolalpha
              << (Version{2, 1, 0} >= Version{2, 0, 5}) << ' ' << (vs[2] == vs[3]) << ' '
              << (vs[0] != vs[1]) << '\n';

    auto r = (1.5 <=> 2.0);
    std::cout << "1.5 <=> 2.0 is less? " << (r < 0) << '\n';

    Vec2 a{1, 2}, b{3, 4};
    Vec2 c = a + b;
    Vec2 d = 2.0 * c;
    std::cout << c.x << ',' << c.y << ' ' << d.x << ',' << d.y << ' ' << (c == Vec2{4, 6}) << '\n';

    Grid g;
    g[1, 2] = 7;
    std::cout << "g[1, 2] = " << g[1, 2] << '\n';
}
