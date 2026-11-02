#include <iostream>
#include <string>
#include <utility>

struct Tracer {
    std::string name;
    explicit Tracer(std::string n) : name{std::move(n)} { std::cout << "  + " << name << '\n'; }
    ~Tracer() { std::cout << "  - " << name << '\n'; }
};

class Effect {
public:
    explicit Effect(std::string name) : name_{std::move(name)}, t_{"Effect base"} {}
    const std::string& name() const { return name_; }
    bool enabled() const { return enabled_; }
    void set_enabled(bool e) { enabled_ = e; }
    void process(int n) { std::cout << "  Effect::process(int " << n << ")\n"; }
    void process(double x) { std::cout << "  Effect::process(double " << x << ")\n"; }
protected:
    int processed_ = 0;                 // visible to derived classes only
private:
    std::string name_;
    bool enabled_ = true;
    Tracer t_;
};

class Gain : public Effect {
public:
    Gain(float g) : Effect{"gain"}, t_{"Gain member"}, gain_{g} { std::cout << "  Gain body\n"; }
    using Effect::process;              // un-hide the base overloads
    void process(float x) { ++processed_; std::cout << "  Gain::process(float " << x * gain_ << ")\n"; }
private:
    Tracer t_;
    float gain_;
};

class Mute : public Effect {
public:
    using Effect::Effect;               // inherit constructors
};

int main() {
    std::cout << "construct:\n";
    {
        Gain g{2.0f};
        g.process(1.5f);
        g.process(7);                   // Effect::process(int), thanks to `using`
        Mute m{"mute"};
        std::cout << "  " << g.name() << ' ' << m.name() << '\n';
        std::cout << "destroy:\n";
    }
}
