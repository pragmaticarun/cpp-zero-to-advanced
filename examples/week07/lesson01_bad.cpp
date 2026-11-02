template <typename T>
T clamp_to(T v, T lo, T hi) { return v < lo ? lo : (hi < v ? hi : v); }
int main() { return static_cast<int>(clamp_to(0.7, 0, 1)); }   // error: conflicting T
