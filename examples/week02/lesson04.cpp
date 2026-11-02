#include <iostream>
#include <string>

struct Noisy {
    std::string name;
    explicit Noisy(std::string n) : name(std::move(n)) { std::cout << "  construct " << name << '\n'; }
    ~Noisy() { std::cout << "  destroy   " << name << '\n'; }
};

namespace media::audio {           // C++17 nested namespace
int counter() {
    static Noisy once{"static-local"};  // constructed on first call only
    static int calls = 0;
    return ++calls;
}
}  // namespace media::audio

Noisy global{"global"};            // static storage: before main, destroyed after main

int main() {
    std::cout << "main starts\n";
    Noisy outer{"outer"};
    {
        Noisy inner{"inner"};
        const int n = media::audio::counter();   // first call constructs the static
        std::cout << "  calls=" << n << '\n';
    }   // inner destroyed here
    using media::audio::counter;
    std::cout << "  calls=" << counter() << '\n';
    std::cout << "main ends\n";
}   // outer destroyed here; then static-local, then global (reverse order)
