#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

struct Track {
    std::string title;
    explicit Track(const std::string& t) : title{t} { std::cout << "  Track(copy title)\n"; }
    explicit Track(std::string&& t) : title{std::move(t)} { std::cout << "  Track(move title)\n"; }
};

template <typename T, typename... Args>
std::unique_ptr<T> make_logged(Args&&... args) {
    std::cout << "make_logged with " << sizeof...(Args) << " arg(s)\n";
    return std::make_unique<T>(std::forward<Args>(args)...);     // perfect forwarding
}

template <typename T>
void bad_wrapper(T&& x) { Track t{x}; }                           // always an lvalue -> copy

template <typename Container>
decltype(auto) first(Container& c) { return c[0]; }              // returns a reference

template <typename T>
void show(T&&) {
    std::cout << (std::is_lvalue_reference_v<T> ? "  T is an lvalue reference\n" : "  T is a non-reference\n");
}

int main() {
    std::string name = "Blue in Green";
    auto a = make_logged<Track>(name);                 // lvalue: copy
    auto b = make_logged<Track>(std::string{"So What"}); // rvalue: move
    std::cout << "bad_wrapper with an rvalue:\n";
    bad_wrapper(std::string{"Freddie Freeloader"});    // copies anyway
    show(name);
    show(std::string{"tmp"});

    std::vector<int> v{1, 2, 3};
    first(v) = 100;                                    // decltype(auto) kept int&
    std::cout << "v[0]=" << v[0] << ", name still \"" << name << "\"\n";
}
