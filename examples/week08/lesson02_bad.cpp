// consteval rejects a non-constant use; UB in constant evaluation is a compile error
#include <string_view>
consteval int len4(std::string_view s) { if (s.size() != 4) throw "need 4"; return 4; }
constexpr int overflow() { int x = 2147483647; return x + 1; }
int main() {
    constexpr int a = len4("RIFFX");   // error: throw in constant evaluation
    constexpr int b = overflow();      // error: signed overflow is UB -> not a constant
    return a + b;
}
