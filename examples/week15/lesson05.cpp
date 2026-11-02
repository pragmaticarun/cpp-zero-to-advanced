#include <chrono>
#include <cstdint>
#include <iostream>
#include <list>
#include <numeric>
#include <vector>

struct Padded { char a; double b; char c; };          // 1 + 7 pad + 8 + 1 + 7 pad = 24
struct Reordered { double b; char a; char c; };        // 8 + 1 + 1 + 6 pad = 16

struct ParticleAoS { float x, y, z, vx, vy, vz; std::uint32_t color; bool alive; float mass, age; };
struct ParticlesSoA { std::vector<float> x, vx; };

template <typename F> double ms(F f) {
    auto t0 = std::chrono::steady_clock::now(); f();
    return std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
}

int main() {
    std::cout << "sizeof Padded=" << sizeof(Padded) << " Reordered=" << sizeof(Reordered) << '\n';

    constexpr std::size_t n = 1'000'000;
    std::vector<ParticleAoS> aos(n, ParticleAoS{0, 0, 0, 1, 0, 0, 0, true, 1, 0});
    ParticlesSoA soa{std::vector<float>(n, 0.0f), std::vector<float>(n, 1.0f)};

    double t_aos = ms([&] { for (auto& p : aos) p.x += p.vx * 0.5f; });
    double t_soa = ms([&] { for (std::size_t i = 0; i < n; ++i) soa.x[i] += soa.vx[i] * 0.5f; });
    std::cout << "positions equal: " << std::boolalpha << (aos[n / 2].x == soa.x[n / 2]) << '\n';

    std::vector<int> v(n, 1);
    std::list<int> l(n, 1);
    long long sv = 0, sl = 0;
    double t_vec = ms([&] { sv = std::accumulate(v.begin(), v.end(), 0LL); });
    double t_list = ms([&] { sl = std::accumulate(l.begin(), l.end(), 0LL); });
    std::cout << "sums " << sv << ' ' << sl << '\n';
    std::cerr << "AoS " << t_aos << " ms, SoA " << t_soa << " ms; vector " << t_vec << " ms, list " << t_list << " ms\n";
}
