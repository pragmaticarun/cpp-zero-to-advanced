#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <type_traits>
#include <variant>
#include <vector>

// Strategy: just a callable
using Interp = std::function<double(double, double, double)>;
double sample(double a, double b, double t, const Interp& how) { return how(a, b, t); }

// Visitor over a closed set of shapes
struct Circle { double r; };
struct Rect { double w, h; };
using Shape = std::variant<Circle, Rect>;
template <typename... Fs> struct overloaded : Fs... { using Fs::operator()...; };

// Observer with weak_ptr: dead listeners are skipped and pruned
class Meter {
public:
    using Listener = std::function<void(double)>;
    void subscribe(const std::shared_ptr<Listener>& l) { listeners_.push_back(l); }
    void publish(double v) {
        std::erase_if(listeners_, [](const auto& w) { return w.expired(); });
        for (auto& w : listeners_) if (auto l = w.lock()) (*l)(v);
    }
    std::size_t count() const { return listeners_.size(); }
private:
    std::vector<std::weak_ptr<Listener>> listeners_;
};

// Factory registry
struct Effect { virtual ~Effect() = default; virtual std::string name() const = 0; };
struct Reverb : Effect { std::string name() const override { return "reverb"; } };
struct Delay : Effect { std::string name() const override { return "delay"; } };
std::map<std::string, std::function<std::unique_ptr<Effect>()>>& registry() {
    static std::map<std::string, std::function<std::unique_ptr<Effect>()>> r{
        {"reverb", [] { return std::make_unique<Reverb>(); }},
        {"delay", [] { return std::make_unique<Delay>(); }}};
    return r;
}

// Scope guard
template <typename F> struct ScopeExit { F f; ~ScopeExit() { f(); } };
template <typename F> ScopeExit(F) -> ScopeExit<F>;

int main() {
    std::cout << "linear " << sample(0, 10, 0.3, [](double a, double b, double t) { return a + (b - a) * t; })
              << ", step " << sample(0, 10, 0.3, [](double a, double b, double t) { return t < 0.5 ? a : b; }) << '\n';

    std::vector<Shape> shapes{Circle{1.0}, Rect{2, 3}};
    for (const auto& s : shapes)
        std::visit(overloaded{[](const Circle& c) { std::cout << "circle area " << 3.14159 * c.r * c.r << '\n'; },
                              [](const Rect& r) { std::cout << "rect area " << r.w * r.h << '\n'; }}, s);

    Meter meter;
    auto keep = std::make_shared<Meter::Listener>([](double v) { std::cout << "ui got " << v << '\n'; });
    meter.subscribe(keep);
    {
        auto temp = std::make_shared<Meter::Listener>([](double v) { std::cout << "logger got " << v << '\n'; });
        meter.subscribe(temp);
        meter.publish(-6.0);
    }                                               // logger destroyed
    meter.publish(-3.0);
    std::cout << "listeners now " << meter.count() << '\n';

    for (const char* n : {"delay", "reverb", "chorus"}) {
        auto it = registry().find(n);
        std::cout << n << " -> " << (it != registry().end() ? it->second()->name() : std::string{"unknown effect"}) << '\n';
    }

    {
        ScopeExit guard{[] { std::cout << "scope guard ran\n"; }};
        std::cout << "doing work\n";
    }
}
