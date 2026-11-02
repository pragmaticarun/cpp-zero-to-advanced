#include <algorithm>
#include <cstddef>
#include <iostream>
#include <utility>

class Buffer {
public:
    explicit Buffer(std::size_t n) : data_{new float[n]{}}, n_{n} { std::cout << "  ctor(" << n << ")\n"; }
    ~Buffer() { delete[] data_; }

    Buffer(const Buffer& other) : data_{new float[other.n_]}, n_{other.n_} {   // deep copy
        std::copy(other.data_, other.data_ + n_, data_);
        std::cout << "  copy ctor\n";
    }
    Buffer& operator=(Buffer other) {          // copy-and-swap: `other` is already a copy
        std::cout << "  copy assign (swap)\n";
        swap(*this, other);
        return *this;
    }                                          // old contents die with `other`
    friend void swap(Buffer& a, Buffer& b) noexcept {
        using std::swap;
        swap(a.data_, b.data_);
        swap(a.n_, b.n_);
    }

    float& operator[](std::size_t i) { return data_[i]; }
    std::size_t size() const { return n_; }

private:
    float* data_;
    std::size_t n_;
};

int main() {
    Buffer a{4};
    a[0] = 1.5f;
    Buffer b = a;            // copy constructor
    b[0] = 9.0f;             // independent copy
    std::cout << "a[0]=" << a[0] << " b[0]=" << b[0] << '\n';

    Buffer c{2};
    c = a;                   // copy assignment
    Buffer& alias = c;
    c = alias;               // self-assignment (through an alias) is safe
    std::cout << "c.size()=" << c.size() << " c[0]=" << c[0] << '\n';
}
