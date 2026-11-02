#include <iostream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

class Playlist {
public:
    void add_bad(const std::string& t) {
        ++count_;                                  // state changed...
        validate(t);                               // ...then a throw: count_ is now wrong
        tracks_.push_back(t);
    }
    void add_good(const std::string& t) {
        validate(t);                               // all throwing work first
        tracks_.push_back(t);                      // strong guarantee by itself
        ++count_;                                  // no-throw commit
    }
    void replace_all(std::vector<std::string> fresh) {   // strong: build aside, swap in
        for (const auto& t : fresh) validate(t);
        tracks_.swap(fresh);
        count_ = static_cast<int>(tracks_.size());
    }
    bool consistent() const { return count_ == static_cast<int>(tracks_.size()); }
private:
    static void validate(const std::string& t) { if (t.empty()) throw std::invalid_argument{"empty title"}; }
    std::vector<std::string> tracks_;
    int count_ = 0;
};

struct Thrower { Thrower() = default; Thrower(Thrower&&) {} };
struct Safe { Safe() = default; Safe(Safe&&) noexcept {} };

int main() {
    Playlist p;
    try { p.add_bad(""); } catch (const std::exception& e) { std::cout << "add_bad threw: " << e.what() << '\n'; }
    std::cout << "consistent after add_bad? " << std::boolalpha << p.consistent() << '\n';

    Playlist q;
    try { q.add_good(""); } catch (const std::exception&) {}
    std::cout << "consistent after add_good? " << q.consistent() << '\n';

    q.add_good("So What");
    try { q.replace_all({"A", "", "C"}); } catch (const std::exception&) {}
    std::cout << "consistent after failed replace_all? " << q.consistent() << '\n';

    std::cout << "noexcept(Thrower move)=" << std::is_nothrow_move_constructible_v<Thrower>
              << " noexcept(Safe move)=" << std::is_nothrow_move_constructible_v<Safe> << '\n';
    std::cout << "noexcept(p.consistent())=" << noexcept(p.consistent()) << '\n';
}
