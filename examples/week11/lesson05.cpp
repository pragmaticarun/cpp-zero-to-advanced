#include <generator>
#include <iostream>
#include <ranges>
#include <string>
#include <utility>
#include <vector>

std::generator<long long> fibonacci() {
    long long a = 0, b = 1;
    while (true) {
        co_yield a;
        a = std::exchange(b, a + b);
    }
}

std::generator<std::string> packets(std::vector<std::string> wire) {   // by value: no dangling
    for (auto& p : wire) {
        if (p == "EOF") co_return;
        co_yield "pkt:" + p;
    }
}

struct Node { std::string name; std::vector<Node> children; };

std::generator<const std::string&> walk(const Node& n) {
    co_yield n.name;
    for (const auto& c : n.children) co_yield std::ranges::elements_of(walk(c));
}

int main() {
    for (auto x : fibonacci() | std::views::drop(5) | std::views::take(5)) std::cout << x << ' ';
    std::cout << '\n';
    for (const auto& p : packets({"a", "b", "EOF", "c"})) std::cout << p << ' ';
    std::cout << '\n';
    Node root{"root", {{"drums", {{"kick", {}}, {"snare", {}}}}, {"bass", {}}}};
    for (const auto& name : walk(root)) std::cout << name << ' ';
    std::cout << '\n';
}
