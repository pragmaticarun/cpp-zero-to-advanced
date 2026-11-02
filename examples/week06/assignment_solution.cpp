#include <iostream>
#include <memory>
#include <span>
#include <vector>

class Effect {
public:
    virtual ~Effect() = default;
    void process(std::span<float> buf) { if (enabled_) do_process(buf); }
    void set_enabled(bool e) { enabled_ = e; }
    virtual std::unique_ptr<Effect> clone() const = 0;
protected:
    Effect() = default;
    Effect(const Effect&) = default;            // usable by clone() in derived classes only
    Effect& operator=(const Effect&) = delete;
private:
    virtual void do_process(std::span<float> buf) = 0;
    bool enabled_ = true;
};

class Gain final : public Effect {
public:
    explicit Gain(float g) : g_{g} {}
    std::unique_ptr<Effect> clone() const override { return std::make_unique<Gain>(*this); }
private:
    void do_process(std::span<float> b) override { for (auto& x : b) x *= g_; }
    float g_;
};

class Clip final : public Effect {
public:
    std::unique_ptr<Effect> clone() const override { return std::make_unique<Clip>(*this); }
private:
    void do_process(std::span<float> b) override { for (auto& x : b) x = x > 1 ? 1 : (x < -1 ? -1 : x); }
};

class Delay final : public Effect {
public:
    Delay(std::size_t samples, float mix) : line_(samples), mix_{mix} {}
    std::unique_ptr<Effect> clone() const override { return std::make_unique<Delay>(*this); }
private:
    void do_process(std::span<float> b) override {
        for (auto& x : b) {
            const float delayed = line_[pos_];
            line_[pos_] = x;
            pos_ = (pos_ + 1) % line_.size();
            x += mix_ * delayed;
        }
    }
    std::vector<float> line_;
    std::size_t pos_ = 0;
    float mix_;
};

using Chain = std::vector<std::unique_ptr<Effect>>;

Chain clone_chain(const Chain& c) {
    Chain out;
    for (const auto& e : c) out.push_back(e->clone());
    return out;
}

void run(Chain& chain, const char* label) {
    std::vector<float> buf{1, 0, 0, 0, 0, 0};
    for (auto& e : chain) e->process(buf);
    std::cout << label << ": ";
    for (float x : buf) std::cout << x << ' ';
    std::cout << '\n';
}

int main() {
    Chain chain;
    chain.push_back(std::make_unique<Gain>(3.0f));
    chain.push_back(std::make_unique<Delay>(2, 0.5f));
    chain.push_back(std::make_unique<Clip>());
    Chain copy = clone_chain(chain);
    run(chain, "original");
    copy[2]->set_enabled(false);
    run(copy, "copy, clip off");
}
