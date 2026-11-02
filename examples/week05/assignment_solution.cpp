#include <cmath>
#include <iostream>
#include <numbers>
#include <string>
#include <utility>
#include <vector>

struct Tally {                       // instrumentation member: counts copies and moves of its owner
    inline static int copies = 0, moves = 0;
    Tally() = default;
    Tally(const Tally&) { ++copies; }
    Tally(Tally&&) noexcept { ++moves; }
    Tally& operator=(const Tally&) { ++copies; return *this; }
    Tally& operator=(Tally&&) noexcept { ++moves; return *this; }
};

class Clip {                         // Rule of Zero: no special members written
public:
    static Clip make_sine(std::string name, float freq, int n) {
        Clip c;
        c.name_ = std::move(name);
        c.samples_.reserve(static_cast<std::size_t>(n));
        for (int i = 0; i < n; ++i)
            c.samples_.push_back(std::sin(2.0f * std::numbers::pi_v<float> * freq * static_cast<float>(i) / 48000.0f));
        return c;                     // NRVO / implicit move
    }
    const std::string& name() const { return name_; }
    std::size_t size() const { return samples_.size(); }
private:
    std::string name_;
    std::vector<float> samples_;
    Tally tally_;
};

class Playlist {
public:
    void add(Clip c) { clips_.push_back(std::move(c)); }   // sink
    void print() const { for (const auto& c : clips_) std::cout << c.name() << '(' << c.size() << ") "; std::cout << '\n'; }
private:
    std::vector<Clip> clips_;
};

int main() {
    Playlist p;
    p.add(Clip::make_sine("A4", 440.0f, 480));
    p.add(Clip::make_sine("C5", 523.25f, 480));
    Clip e = Clip::make_sine("E5", 659.25f, 480);
    p.add(std::move(e));
    p.print();
    std::cout << "copies=" << Tally::copies << " moves=" << Tally::moves << '\n';
}
