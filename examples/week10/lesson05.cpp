#include <cstddef>
#include <iostream>
#include <mdspan>
#include <span>
#include <vector>

float peak(std::span<const float> s) {
    float p = 0;
    for (float x : s) p = (x < 0 ? -x : x) > p ? (x < 0 ? -x : x) : p;
    return p;
}

int main() {
    std::vector<float> interleaved{0.1f, -0.9f, 0.4f, 0.2f, -0.3f, 0.8f};   // L R L R L R
    std::cout << "peak(all)=" << peak(interleaved) << " peak(first 2)=" << peak(std::span{interleaved}.first(2)) << '\n';

    // View the same memory as frames x channels
    std::mdspan audio(interleaved.data(), 3, 2);
    for (std::size_t ch = 0; ch < audio.extent(1); ++ch) {
        float p = 0;
        for (std::size_t f = 0; f < audio.extent(0); ++f) {
            float a = audio[f, ch] < 0 ? -audio[f, ch] : audio[f, ch];
            if (a > p) p = a;
        }
        std::cout << "channel " << ch << " peak " << p << '\n';
    }

    std::vector<int> pixels(4 * 3, 0);
    std::mdspan img(pixels.data(), 3, 4);           // 3 rows x 4 cols, row-major
    img[1, 2] = 255;
    std::cout << "pixel (1,2) is element " << (&img[1, 2] - pixels.data()) << " in memory\n";

    std::mdspan<int, std::extents<std::size_t, 3, 4>, std::layout_left> col_major(pixels.data());
    std::cout << "column-major (1,2) is element " << (&col_major[1, 2] - pixels.data()) << '\n';
}
