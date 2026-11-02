#include <iostream>
#include <memory>
#include <span>
#include <string>
#include <vector>

class Effect {
public:
    Effect() { std::cout << "Effect ctor sees name(): " << name() << '\n'; }   // calls Effect::name!
    virtual ~Effect() = default;
    virtual void process(std::span<float> buf) = 0;
    virtual std::string name() const { return "effect"; }
};

class Gain final : public Effect {
public:
    explicit Gain(float g) : g_{g} {}
    void process(std::span<float> buf) override { for (auto& x : buf) x *= g_; }
    std::string name() const override { return "gain"; }
private:
    float g_;
};

class Clip : public Effect {
public:
    void process(std::span<float> buf) override {
        for (auto& x : buf) x = x > 1.0f ? 1.0f : (x < -1.0f ? -1.0f : x);
    }
    std::string name() const override { return "clip"; }
};

struct NoVirtual { float g; };
struct WithVirtual { virtual ~WithVirtual() = default; float g; };

int main() {
    std::vector<std::unique_ptr<Effect>> chain;
    chain.push_back(std::make_unique<Gain>(3.0f));
    chain.push_back(std::make_unique<Clip>());

    std::vector<float> buf{0.1f, 0.5f, -0.6f};
    for (const auto& e : chain) {          // dynamic dispatch
        e->process(buf);
        std::cout << e->name() << ": ";
        for (float x : buf) std::cout << x << ' ';
        std::cout << '\n';
    }
    std::cout << "sizeof(NoVirtual)=" << sizeof(NoVirtual) << " sizeof(WithVirtual)=" << sizeof(WithVirtual) << '\n';
}
