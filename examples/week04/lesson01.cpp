#include <iostream>

class Volume {
public:
    explicit Volume(int level = 50) : level_{clamp(level)} {}

    void set(int level) { level_ = clamp(level); }
    void louder(int step = 10) { set(level_ + step); }
    int get() const { return level_; }          // const: callable on const objects
    bool muted() const { return level_ == 0; }

private:
    static int clamp(int v) { return v < 0 ? 0 : (v > 100 ? 100 : v); }
    int level_;                                  // invariant: 0 <= level_ <= 100
};

void show(const Volume& v) {                     // only const members are callable here
    std::cout << "volume " << v.get() << (v.muted() ? " (muted)" : "") << '\n';
}

int main() {
    Volume v{70};
    show(v);
    v.louder(); v.louder(); v.louder();
    show(v);                                     // clamped to 100
    v.set(-5);
    show(v);                                     // clamped to 0
}
