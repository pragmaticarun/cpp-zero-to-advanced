#include <iostream>
#include <thread>

int main() {
    int counter = 0;                                   // shared, unprotected
    {
        std::jthread a{[&] { for (int i = 0; i < 100000; ++i) ++counter; }};
        std::jthread b{[&] { for (int i = 0; i < 100000; ++i) ++counter; }};
    }
    std::cout << "counter = " << counter << " (expected 200000)\n";   // data race: UB
}
