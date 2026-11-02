#include <iostream>
#include <string>
#include <type_traits>
#include <utility>

template <class T> constexpr const char* category() {
    if constexpr (std::is_lvalue_reference_v<T>) return "lvalue";
    else if constexpr (std::is_rvalue_reference_v<T>) return "xvalue";
    else return "prvalue";
}
#define CATEGORY(...) category<decltype((__VA_ARGS__))>()

void take(const std::string& s) { std::cout << "  take(const&)  [copy if needed]: " << s << '\n'; }
void take(std::string&& s) {
    std::cout << "  take(&&)      [may steal]: " << s << '\n';
    std::cout << "    inside, `s` is an " << CATEGORY(s) << '\n';
}

std::string make() { return "made"; }

int main() {
    std::string name = "named";
    int x = 1;
    std::cout << "x: " << CATEGORY(x) << ", 42: " << CATEGORY(42) << ", x + 1: " << CATEGORY(x + 1)
              << ", std::move(x): " << CATEGORY(std::move(x)) << ", make(): " << CATEGORY(make()) << '\n';

    take(name);                 // lvalue  -> const&
    take(make());               // prvalue -> &&
    take(std::string{"temp"});  // prvalue -> &&
    take(std::move(name));      // xvalue  -> &&
}
