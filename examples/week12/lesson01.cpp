#include <cstdio>
#include <iostream>
#include <memory>
#include <string>
#include <utility>

struct Codec {
    explicit Codec(int rate) : rate{rate} { std::cout << "  Codec(" << rate << ") opened\n"; }
    ~Codec() { std::cout << "  Codec(" << rate << ") closed\n"; }
    int rate;
};

struct FileCloser { void operator()(std::FILE* f) const noexcept { if (f) { std::fclose(f); std::cout << "  file closed\n"; } } };
using File = std::unique_ptr<std::FILE, FileCloser>;

// A C-style API that returns a resource through an out-parameter
int c_open_codec(int rate, Codec** out) { *out = new Codec{rate}; return 0; }

void use(const Codec& c) { std::cout << "  using codec at " << c.rate << '\n'; }      // borrows
void sink(std::unique_ptr<Codec> c) { std::cout << "  sink took " << c->rate << '\n'; } // takes ownership

int main() {
    {
        auto a = std::make_unique<Codec>(44100);
        use(*a);
        auto b = std::move(a);                                   // transfer
        std::cout << "  a is " << (a ? "set" : "null") << '\n';
        sink(std::move(b));                                      // destroyed at the end of sink
        std::cout << "after sink\n";
    }
    {
        File f{std::tmpfile()};
        std::fputs("hello", f.get());
        std::cout << "  sizeof(File)==sizeof(FILE*)? " << std::boolalpha << (sizeof(File) == sizeof(std::FILE*)) << '\n';
    }
    {
        std::unique_ptr<Codec> c;
        c_open_codec(96000, std::out_ptr(c));                    // C++23
        std::cout << "  out_ptr filled codec at " << c->rate << '\n';
    }
    auto buf = std::make_unique_for_overwrite<char[]>(4096);    // no zeroing: we'll overwrite it
    buf[0] = 'x';
    std::cout << "buffer starts with " << buf[0] << '\n';
}
