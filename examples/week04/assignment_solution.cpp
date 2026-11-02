#include <compare>
#include <iostream>
#include <numeric>
#include <stdexcept>

class Rational {
public:
    Rational(long long n = 0, long long d = 1) : num_{n}, den_{d} {   // implicit from integers is natural here
        if (den_ == 0) throw std::invalid_argument("zero denominator");
        normalize();
    }
    long long num() const { return num_; }
    long long den() const { return den_; }

    Rational& operator+=(const Rational& o) { num_ = num_ * o.den_ + o.num_ * den_; den_ *= o.den_; normalize(); return *this; }
    Rational& operator-=(const Rational& o) { return *this += Rational{-o.num_, o.den_}; }
    Rational& operator*=(const Rational& o) { num_ *= o.num_; den_ *= o.den_; normalize(); return *this; }
    Rational& operator/=(const Rational& o) { return *this *= Rational{o.den_, o.num_}; }

    friend Rational operator+(Rational a, const Rational& b) { return a += b; }
    friend Rational operator-(Rational a, const Rational& b) { return a -= b; }
    friend Rational operator*(Rational a, const Rational& b) { return a *= b; }
    friend Rational operator/(Rational a, const Rational& b) { return a /= b; }

    bool operator==(const Rational&) const = default;   // OK: always reduced
    std::strong_ordering operator<=>(const Rational& o) const { return num_ * o.den_ <=> o.num_ * den_; }

    explicit operator double() const { return static_cast<double>(num_) / static_cast<double>(den_); }
    friend std::ostream& operator<<(std::ostream& os, const Rational& r) { return os << r.num_ << '/' << r.den_; }

private:
    void normalize() {
        if (den_ < 0) { num_ = -num_; den_ = -den_; }
        const long long g = std::gcd(num_, den_);
        if (g > 1) { num_ /= g; den_ /= g; }
    }
    long long num_, den_;
};

int main() {
    Rational a{1, 2}, b{3, -4};
    std::cout << a << " + " << b << " = " << a + b << '\n';
    std::cout << a << " * " << b << " = " << a * b << '\n';
    std::cout << a << " / " << b << " = " << a / b << '\n';
    std::cout << std::boolalpha << (Rational{2, 4} == a) << ' ' << (b < a) << ' ' << (a + 1 > Rational{3, 2}) << '\n';
    std::cout << static_cast<double>(Rational{1, 3}) << '\n';
    try { Rational bad{1, 0}; } catch (const std::invalid_argument& e) { std::cout << "error: " << e.what() << '\n'; }
}
