#include <functional>
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

struct Track { std::string title; int seconds; int duration_min() const { return seconds / 60; } };

class EventBus {                                     // stored callbacks
public:
    void subscribe(std::function<void(const std::string&)> cb) { subs_.push_back(std::move(cb)); }
    void publish(const std::string& e) const { for (const auto& s : subs_) s(e); }
private:
    std::vector<std::function<void(const std::string&)>> subs_;
};

// Hand-written type erasure: anything with a draw() member
class AnyDrawable {
public:
    template <typename T>
    AnyDrawable(T obj) : self_{std::make_unique<Model<T>>(std::move(obj))} {}
    void draw() const { self_->draw(); }
private:
    struct Concept { virtual ~Concept() = default; virtual void draw() const = 0; };
    template <typename T>
    struct Model final : Concept {
        explicit Model(T o) : obj{std::move(o)} {}
        void draw() const override { obj.draw(); }
        T obj;
    };
    std::unique_ptr<Concept> self_;
};
struct Circle { void draw() const { std::cout << "  circle\n"; } };
struct Label { std::string text; void draw() const { std::cout << "  label: " << text << '\n'; } };

int main() {
    EventBus bus;
    int received = 0;
    bus.subscribe([&received](const std::string& e) { ++received; std::cout << "ui got " << e << '\n'; });
    bus.subscribe([](const std::string& e) { std::cout << "logger got " << e << '\n'; });
    bus.publish("track-changed");

    std::move_only_function<int()> job = [p = std::make_unique<int>(41)] { return *p + 1; };
    std::cout << "move_only_function: " << job() << '\n';

    Track t{"So What", 562};
    std::cout << std::invoke(&Track::title, t) << ' ' << std::invoke(&Track::duration_min, t) << "min\n";

    auto add = [](int a, int b) { return a + b; };
    auto add10 = std::bind_front(add, 10);
    std::cout << add10(5) << ' ' << received << '\n';

    std::vector<AnyDrawable> scene{Circle{}, Label{"hello"}};
    for (const auto& d : scene) d.draw();
}
