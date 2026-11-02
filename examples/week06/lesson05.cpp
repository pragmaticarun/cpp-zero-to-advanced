#include <any>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <typeindex>
#include <typeinfo>
#include <vector>

struct Effect { virtual ~Effect() = default; };
struct Gain : Effect { float g = 1.0f; };
struct Reverb : Effect { float room = 0.5f; };

int main() {
    std::vector<std::unique_ptr<Effect>> fx;
    fx.push_back(std::make_unique<Gain>());
    fx.push_back(std::make_unique<Reverb>());

    std::map<std::type_index, std::string> names{{typeid(Gain), "Gain"}, {typeid(Reverb), "Reverb"}};
    for (const auto& e : fx) {
        const Effect& ref = *e;
        std::cout << "dynamic type: " << names[typeid(ref)];
        if (auto* r = dynamic_cast<Reverb*>(e.get())) std::cout << " (room=" << r->room << ')';
        std::cout << '\n';
    }

    try {
        Effect& first = *fx[0];
        auto& r = dynamic_cast<Reverb&>(first);   // it's a Gain: throws
        (void)r;
    } catch (const std::bad_cast&) {
        std::cout << "bad_cast: first effect is not a Reverb\n";
    }

    std::map<std::string, std::any> props{{"rate", 48000}, {"codec", std::string{"opus"}}, {"vbr", true}};
    std::cout << "rate=" << std::any_cast<int>(props["rate"])
              << " codec=" << std::any_cast<std::string>(props["codec"]) << '\n';
    try {
        std::cout << std::any_cast<double>(props["rate"]);
    } catch (const std::bad_any_cast&) {
        std::cout << "bad_any_cast: rate holds an int, not a double\n";
    }
}
