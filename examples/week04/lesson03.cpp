#include <cstdio>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>

class File {
public:
    File(const char* path, const char* mode) : f_{std::fopen(path, mode)} {
        if (!f_) throw std::runtime_error(std::string{"cannot open "} + path);
        std::cout << "  opened " << path << '\n';
    }
    ~File() { std::fclose(f_); std::cout << "  closed\n"; }
    File(const File&) = delete;              // one owner only
    File& operator=(const File&) = delete;

    void write(const std::string& s) { std::fputs(s.c_str(), f_); }

private:
    std::FILE* f_;
};

template <class F>
class ScopeGuard {                           // runs an action when the scope ends
public:
    explicit ScopeGuard(F f) : f_{std::move(f)} {}
    ~ScopeGuard() { f_(); }
    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;
private:
    F f_;
};

void process(bool fail) {
    File out{"/tmp/raii_demo.txt", "w"};
    ScopeGuard guard{[] { std::cout << "  guard: cleanup step\n"; }};
    out.write("hello\n");
    if (fail) throw std::runtime_error("encoding failed");
    std::cout << "  done\n";
}

int main() {
    std::cout << "normal run:\n";
    process(false);
    std::cout << "failing run:\n";
    try {
        process(true);
    } catch (const std::exception& e) {
        std::cout << "  caught: " << e.what() << '\n';
    }
}
