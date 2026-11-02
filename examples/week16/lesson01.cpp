#include <cmath>
#include <cstdio>
#include <iostream>
#include <new>
#include <stdexcept>
#include <string>
#include <vector>

// ===== dsp.h — what C (and every FFI) sees =====
extern "C" {
typedef struct dsp_mixer dsp_mixer;                       // opaque handle
typedef void (*dsp_level_cb)(double level, void* user);
enum { DSP_OK = 0, DSP_ERR_ARG = 1, DSP_ERR_INTERNAL = 2 };
dsp_mixer* dsp_mixer_create(int channels);
void dsp_mixer_destroy(dsp_mixer* m);
int dsp_mixer_process(dsp_mixer* m, const float* samples, int n, dsp_level_cb cb, void* user);
}

// ===== dsp.cpp — the C++ implementation =====
struct dsp_mixer {
    int channels;
    std::vector<float> scratch;
    double process(const float* s, int n) {
        if (n < 0) throw std::invalid_argument{"negative length"};
        scratch.assign(s, s + n);
        double sum = 0; for (float x : scratch) sum += static_cast<double>(x) * x;
        return n ? std::sqrt(sum / n) : 0.0;
    }
};

extern "C" dsp_mixer* dsp_mixer_create(int channels) {
    try { return new dsp_mixer{channels, {}}; } catch (...) { return nullptr; }
}
extern "C" void dsp_mixer_destroy(dsp_mixer* m) { delete m; }
extern "C" int dsp_mixer_process(dsp_mixer* m, const float* s, int n, dsp_level_cb cb, void* user) {
    if (!m || (!s && n > 0)) return DSP_ERR_ARG;
    try {                                                 // no exception may escape into C
        double level = m->process(s, n);
        if (cb) cb(level, user);
        return DSP_OK;
    } catch (const std::invalid_argument&) { return DSP_ERR_ARG; }
    catch (...) { return DSP_ERR_INTERNAL; }
}

// ===== a "C client" =====
static void on_level(double level, void* user) {
    *static_cast<double*>(user) = level;
}

int main() {
    dsp_mixer* m = dsp_mixer_create(2);
    float samples[] = {0.5f, -0.5f, 0.5f, -0.5f};
    double level = 0;
    int rc = dsp_mixer_process(m, samples, 4, on_level, &level);
    std::printf("rc=%d level=%.3f\n", rc, level);
    rc = dsp_mixer_process(m, samples, -1, on_level, &level);
    std::printf("negative length -> rc=%d (exception stayed inside C++)\n", rc);
    std::printf("null handle -> rc=%d\n", dsp_mixer_process(nullptr, samples, 4, nullptr, nullptr));
    dsp_mixer_destroy(m);
}
