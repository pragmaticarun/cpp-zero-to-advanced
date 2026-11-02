#include <iostream>
#include <string>
#include <utility>

struct Loud {
    std::string tag;
    explicit Loud(std::string t) : tag{std::move(t)} { std::cout << "  construct " << tag << '\n'; }
    Loud(const Loud& o) : tag{o.tag} { std::cout << "  COPY " << tag << '\n'; }
    Loud(Loud&& o) noexcept : tag{std::move(o.tag)} { std::cout << "  move " << tag << '\n'; }
};

Loud make_prvalue() { return Loud{"prvalue"}; }          // guaranteed elision (C++17)
Loud make_named() { Loud w{"named"}; w.tag += "!"; return w; }   // NRVO in practice
Loud make_either(bool b) {
    Loud x{"x"}, y{"y"};
    if (b) return x;     // two candidates: no NRVO, but implicit move (never a copy)
    return y;
}

class Holder {
public:
    explicit Holder(Loud l) : l_{std::move(l)} {}   // sink parameter
private:
    Loud l_;
};

int main() {
    std::cout << "prvalue:\n";  Loud a = make_prvalue();
    std::cout << "named:\n";    Loud b = make_named();
    std::cout << "either:\n";   Loud c = make_either(true);
    std::cout << "sink from lvalue:\n";
    Holder h1{a};                    // copy into parameter, then move
    std::cout << "sink from rvalue:\n";
    Holder h2{std::move(b)};         // move into parameter, then move
    (void)c; (void)h1; (void)h2;
}
