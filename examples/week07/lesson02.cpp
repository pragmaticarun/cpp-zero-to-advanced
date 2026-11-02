#include <array>
#include <cstddef>
#include <iostream>
#include <string>
#include <vector>

template <typename T, std::size_t N>
class Window {                                    // fixed-size rolling window
public:
    void push(T v) { data_[next_ % N] = v; ++next_; }
    std::size_t size() const { return next_ < N ? next_ : N; }
    T mean() const {                              // only instantiated if used
        T total{};
        for (std::size_t i = 0; i < size(); ++i) total += data_[i];
        return total / static_cast<T>(size());
    }
private:
    std::array<T, N> data_{};
    std::size_t next_ = 0;
};

template <typename T> struct TypeName { static std::string get() { return "unknown"; } };
template <> struct TypeName<int> { static std::string get() { return "int"; } };          // full
template <> struct TypeName<float> { static std::string get() { return "float"; } };
template <typename T> struct TypeName<T*> {                                              // partial
    static std::string get() { return "pointer to " + TypeName<T>::get(); }
};

template <typename T>
struct Tagged {
    T value;
    std::string tag;
};
Tagged(const char*, const char*) -> Tagged<std::string>;   // deduction guide

template <typename T> constexpr T pi = T(3.14159265358979323846L);   // variable template
template <typename T> using Grid = std::vector<std::vector<T>>;      // alias template

int main() {
    Window<float, 4> w;
    for (float x : {1.0f, 2.0f, 3.0f, 4.0f, 10.0f}) w.push(x);
    std::cout << "mean of last 4: " << w.mean() << '\n';

    Window<std::string, 2> names;                 // fine: mean() never instantiated
    names.push("a");
    std::cout << "names.size()=" << names.size() << '\n';

    std::cout << TypeName<int>::get() << ", " << TypeName<float**>::get() << ", "
              << TypeName<double>::get() << '\n';

    std::pair p{1, 2.5};                          // CTAD: pair<int, double>
    Tagged t{"hello", "greeting"};                // guide: Tagged<std::string>
    std::cout << p.second << ' ' << t.value.size() << '\n';
    std::cout << pi<float> << ' ' << pi<double> << '\n';
    Grid<int> g(2, std::vector<int>(3, 7));
    std::cout << g.size() << 'x' << g[0].size() << '\n';
}
