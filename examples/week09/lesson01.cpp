#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>

struct Guard {
    std::string name;
    explicit Guard(std::string n) : name{std::move(n)} {}
    ~Guard() { std::cout << "  ~Guard(" << name << ")\n"; }
};

class ParseError : public std::runtime_error {
public:
    ParseError(const std::string& what, int line) : std::runtime_error{what}, line_{line} {}
    int line() const { return line_; }
private:
    int line_;
};

int parse_duration(const std::string& field, int line) {
    Guard g{"parse_duration"};
    std::size_t used = 0;
    int v = std::stoi(field, &used);                  // may throw std::invalid_argument
    if (used != field.size()) throw ParseError{"trailing junk in '" + field + "'", line};
    return v;
}

void load_playlist() {
    Guard g{"load_playlist"};
    try {
        parse_duration("12x", 7);
    } catch (...) {
        std::throw_with_nested(std::runtime_error{"while loading playlist.m3u"});
    }
}

void print_nested(const std::exception& e, int depth = 0) {
    std::cout << std::string(depth * 2, ' ') << "- " << e.what() << '\n';
    try { std::rethrow_if_nested(e); }
    catch (const std::exception& inner) { print_nested(inner, depth + 1); }
}

int main() {
    try {
        load_playlist();
    } catch (const std::exception& e) {
        std::cout << "caught:\n";
        print_nested(e);
    }

    try {
        parse_duration("abc", 3);
    } catch (const ParseError& e) {                   // most specific first
        std::cout << "ParseError at line " << e.line() << '\n';
    } catch (const std::invalid_argument& e) {
        std::cout << "invalid_argument from stoi\n";
    }

    std::exception_ptr saved;
    try { throw std::out_of_range{"index 9"}; } catch (...) { saved = std::current_exception(); }
    try { std::rethrow_exception(saved); }
    catch (const std::logic_error& e) { std::cout << "transported: " << e.what() << '\n'; }
}
