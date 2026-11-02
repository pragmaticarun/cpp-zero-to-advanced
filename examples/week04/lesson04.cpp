#include <iostream>
#include <string>
#include <utility>
#include <vector>

class Millis {
public:
    explicit Millis(long v) : value_{v} {}
    long count() const { return value_; }
private:
    long value_;
};

class Codec {
public:
    explicit Codec(std::string name) : name_{std::move(name)} { ++instances; }
    ~Codec() { --instances; }
    Codec(const Codec&) = delete;
    Codec& operator=(const Codec&) = delete;

    explicit operator bool() const { return !name_.empty(); }   // "is valid?"
    inline static int instances = 0;                              // shared by all Codecs

    friend std::ostream& operator<<(std::ostream& os, const Codec& c) {   // friend: sees name_
        return os << "Codec(" << c.name_ << ")";
    }

    struct Stats { int frames = 0; };                              // nested class
    Stats stats;
private:
    std::string name_;
};

void wait(Millis m) { std::cout << "wait " << m.count() << " ms\n"; }

int main() {
    wait(Millis{20});
    // wait(20);   // would not compile: constructor is explicit

    Codec opus{"opus"}, none{""};
    std::cout << opus << " valid=" << static_cast<bool>(opus) << ", none valid=" << (none ? "yes" : "no")
              << ", instances=" << Codec::instances << '\n';

    struct Counter { int n = 0; void hit() { ++n; } };             // local class
    Counter c;
    for (int i = 0; i < 3; ++i) c.hit();
    opus.stats.frames = c.n;
    std::cout << "frames=" << opus.stats.frames << '\n';
}
