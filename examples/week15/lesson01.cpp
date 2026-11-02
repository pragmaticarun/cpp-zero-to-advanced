#include <iostream>
#include <version>          // defines all __cpp_lib_* macros

#if __has_include(<expected>)
#include <expected>
#endif

int main() {
#ifdef __cpp_lib_expected
    std::cout << "std::expected available (" << __cpp_lib_expected << ")\n";
#else
    std::cout << "std::expected not available in this mode\n";
#endif
#ifdef __cpp_concepts
    std::cout << "concepts: yes\n";
#endif
    std::cout << "__cplusplus = " << (__cplusplus >= 202002L ? ">= C++20" : "< C++20") << '\n';
}
