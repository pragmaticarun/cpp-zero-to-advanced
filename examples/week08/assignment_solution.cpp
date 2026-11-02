#include <concepts>
#include <functional>
#include <iostream>
#include <string_view>
#include <typeindex>
#include <unordered_map>
#include <vector>

template <typename E>
concept Event = std::copyable<E> && requires { { E::name } -> std::convertible_to<std::string_view>; };

class Dispatcher {
public:
    template <Event E, std::invocable<const E&> F>
    void on(F handler) {
        handlers_[typeid(E)].push_back([h = std::move(handler)](const void* p) { h(*static_cast<const E*>(p)); });
    }
    template <Event E>
    void emit(const E& e) const {
        auto it = handlers_.find(typeid(E));
        const std::size_t n = it == handlers_.end() ? 0 : it->second.size();
        if (n) for (const auto& h : it->second) h(&e);
        std::cout << "  [" << E::name << ": " << n << " handler(s)]\n";
    }
private:
    std::unordered_map<std::type_index, std::vector<std::function<void(const void*)>>> handlers_;
};

struct KeyPressed { static constexpr std::string_view name = "KeyPressed"; char key; };
struct Resized { static constexpr std::string_view name = "Resized"; int w, h; };

int main() {
    Dispatcher d;
    int keys = 0;
    d.on<KeyPressed>([&keys](const KeyPressed& e) { ++keys; std::cout << "key " << e.key << '\n'; });
    d.on<KeyPressed>([](const KeyPressed&) { std::cout << "beep\n"; });
    d.emit(KeyPressed{'a'});
    d.emit(Resized{800, 600});
    d.on<Resized>([](const Resized& r) { std::cout << "resized to " << r.w << 'x' << r.h << '\n'; });
    d.emit(Resized{1024, 768});
    std::cout << "keys=" << keys << '\n';
}
