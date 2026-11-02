#include <iostream>

struct Frame { int width; int height; };

void describe(const Frame* f) {       // pointer: may be null
    if (f == nullptr) { std::cout << "no frame\n"; return; }
    std::cout << f->width << 'x' << f->height << '\n';   // f->width == (*f).width
}

int main() {
    int level = 42;
    int* p = &level;
    *p = 7;
    std::cout << "level=" << level << '\n';

    int samples[5] = {10, 20, 30, 40, 50};
    int* first = samples;              // array decays to pointer to first element
    int* last = samples + 4;
    std::cout << "*(first+2)=" << *(first + 2) << " first[3]=" << first[3]
              << " distance=" << (last - first) << '\n';

    for (const int* it = samples; it != samples + 5; ++it)   // one-past-the-end is OK to form
        std::cout << *it << ' ';
    std::cout << '\n';

    const int* ro = &level;   // can't write through ro
    ro = &samples[0];         // but can re-point it
    int* const fixed = &level;
    *fixed = 99;              // can write, can't re-point
    std::cout << *ro << ' ' << level << '\n';

    Frame hd{1280, 720};
    describe(&hd);
    describe(nullptr);
}
