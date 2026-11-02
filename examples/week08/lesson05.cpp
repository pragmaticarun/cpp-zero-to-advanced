#include <cstddef>
#include <iostream>
#include <string>
#include <tuple>
#include <utility>

template <typename Derived>
struct Shape {                                         // CRTP static interface
    double area() const { return static_cast<const Derived&>(*this).area_impl(); }
};
struct Square : Shape<Square> { double s; explicit Square(double x) : s{x} {} double area_impl() const { return s * s; } };
struct Circle : Shape<Circle> { double r; explicit Circle(double x) : r{x} {} double area_impl() const { return 3.14159 * r * r; } };

template <typename T>
double total_area(const Shape<T>& a, const Shape<T>& b) { return a.area() + b.area(); }

template <typename Derived>
struct InstanceCounter {                               // CRTP mixin: per-class counter
    inline static int count = 0;
    InstanceCounter() { ++count; }
};
struct Widget : InstanceCounter<Widget> {};
struct Gadget : InstanceCounter<Gadget> {};

struct Buffer {
    std::string data = "abc";
    template <typename Self>
    auto& get(this Self& self) { return self.data; }    // deducing this: const and non-const in one
};

struct Base {
    void describe(this const auto& self) { std::cout << "I am " << self.name() << '\n'; }
};
struct Mic : Base { std::string name() const { return "a microphone"; } };

template <typename Tuple, std::size_t... I>
void print_tuple_impl(const Tuple& t, std::index_sequence<I...>) {
    ((std::cout << (I == 0 ? "" : ", ") << std::get<I>(t)), ...);
}
template <typename... Ts>
void print_tuple(const std::tuple<Ts...>& t) {
    std::cout << '(';
    print_tuple_impl(t, std::index_sequence_for<Ts...>{});
    std::cout << ")\n";
}

int main() {
    std::cout << total_area(Square{2}, Square{3}) << ' ' << Circle{1}.area() << '\n';
    Widget w1, w2; Gadget g1;
    std::cout << "widgets=" << Widget::count << " gadgets=" << Gadget::count << '\n';

    Buffer b;
    b.get() += "d";
    const Buffer& cb = b;
    std::cout << cb.get() << '\n';                     // const version, same function

    Mic{}.describe();

    auto fib = [](this auto self, int n) -> int { return n < 2 ? n : self(n - 1) + self(n - 2); };  // recursive lambda
    std::cout << "fib(10)=" << fib(10) << '\n';
    print_tuple(std::tuple{1, 2.5, std::string{"three"}});
    (void)w1; (void)w2; (void)g1;
}
