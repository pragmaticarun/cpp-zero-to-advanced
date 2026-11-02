#include <iostream>
#include <memory>
#include <vector>

struct Frame {
    int w, h;
    std::vector<unsigned char> pixels;
    Frame(int w_, int h_) : w(w_), h(h_), pixels(static_cast<std::size_t>(w_ * h_)) {}
};

int main() {
    // Manual (the old way): works, but every exit path must remember delete[].
    int n = 4;
    int* raw = new int[n]{};
    raw[0] = 1;
    delete[] raw;

    // Modern: containers and smart pointers own memory.
    std::vector<int> v(static_cast<std::size_t>(n));   // n zeroed ints, freed automatically
    v[0] = 1;
    auto frame = std::make_unique<Frame>(640, 480);    // heap object, freed automatically
    std::cout << "frame " << frame->w << 'x' << frame->h << " bytes=" << frame->pixels.size()
              << " v[0]=" << v[0] << '\n';
}   // frame and v cleaned up here, in reverse order
