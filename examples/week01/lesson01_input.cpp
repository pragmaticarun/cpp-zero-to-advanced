#include <iostream>
#include <string>

int main() {
    std::cout << "What's your name? ";
    std::string name;
    if (!(std::cin >> name)) {   // reading can fail (e.g. end of input)
        name = "friend";
    }
    std::cout << "\nNice to meet you, " << name << "!\n";
}
