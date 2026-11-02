#include <array>
#include <cstddef>
#include <cstdlib>
#include <iostream>
#include <memory_resource>
#include <new>
#include <string>
#include <vector>

static std::size_t g_allocs = 0;
void* operator new(std::size_t n) {                     // replaced global operator new: count calls
    ++g_allocs;
    if (void* p = std::malloc(n ? n : 1)) return p;
    throw std::bad_alloc{};
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }

int main() {
    std::size_t before = g_allocs;
    {
        std::vector<std::string> v;
        for (int i = 0; i < 4; ++i) v.push_back("a fairly long string number " + std::to_string(i));
    }
    std::cout << "std::vector<std::string>: " << (g_allocs - before > 0 ? "heap allocations happened" : "no heap") << '\n';

    alignas(std::max_align_t) std::array<std::byte, 4096> stack_buf;
    before = g_allocs;
    {
        std::pmr::monotonic_buffer_resource arena{stack_buf.data(), stack_buf.size(), std::pmr::null_memory_resource()};
        std::pmr::vector<std::pmr::string> v{&arena};
        v.reserve(4);
        for (int i = 0; i < 4; ++i) {
            std::pmr::string s{"a fairly long string number ", &arena};
            s += static_cast<char>('0' + i);
            v.push_back(std::move(s));
        }
        std::cout << "pmr in arena: " << v.size() << " strings, last = \"" << v.back() << "\"\n";
        std::cout << "element uses the same arena? " << std::boolalpha
                  << (v.back().get_allocator().resource() == &arena) << '\n';
    }
    std::cout << "global allocations during pmr block: " << (g_allocs - before) << '\n';

    try {
        std::array<std::byte, 16> tiny;
        std::pmr::monotonic_buffer_resource small{tiny.data(), tiny.size(), std::pmr::null_memory_resource()};
        std::pmr::vector<int> v{&small};
        v.resize(100);                                   // needs more than 16 bytes
    } catch (const std::bad_alloc&) {
        std::cout << "null_memory_resource caught an overflow of the arena\n";
    }
}
