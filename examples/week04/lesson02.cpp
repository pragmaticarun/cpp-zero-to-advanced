#include <iostream>
#include <string>
#include <utility>
#include <vector>

class Stream {
public:
    Stream(std::string name, int rate) : name_{std::move(name)}, rate_{rate} {
        std::cout << "open " << name_ << " @" << rate_ << " ch=" << channels_ << '\n';
    }
    explicit Stream(std::string name) : Stream(std::move(name), 48'000) {}   // delegating
    Stream(bool) = delete;                                                  // forbid Stream(true)
    ~Stream() { std::cout << "close " << name_ << '\n'; }

private:
    std::string name_;
    int rate_;
    int channels_ = 2;     // default member initializer
};

struct Point { int x = 0, y = 0; Point() = default; Point(int x_, int y_) : x{x_}, y{y_} {} };

int main() {
    Stream a{"mic", 16'000};
    Stream b{std::string{"speaker"}};   // see the "surprise" box: Stream b{"speaker"} would pick Stream(bool)!

    std::vector<int> paren(3, 7), brace{3, 7};
    std::cout << "paren size=" << paren.size() << " brace size=" << brace.size() << '\n';

    int zero{};         // value-initialized: 0
    Point p{};          // default constructor
    Point q{1, 2};
    std::cout << zero << ' ' << p.x << ',' << p.y << ' ' << q.x << ',' << q.y << '\n';
}   // b closes first, then a
