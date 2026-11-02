#include <iostream>

struct AudioSink { virtual ~AudioSink() = default; virtual void write(int n) = 0; };
struct Controllable { virtual ~Controllable() = default; virtual void pause() = 0; };

class Player : public AudioSink, public Controllable {      // implements two interfaces
public:
    void write(int n) override { std::cout << "write " << n << '\n'; }
    void pause() override { std::cout << "paused\n"; }
};

struct Device { int id = 0; explicit Device(int i) : id{i} {} };
struct Input : virtual Device { Input() : Device{1} {} };
struct Output : virtual Device { Output() : Device{2} {} };
struct Duplex : Input, Output { Duplex() : Device{42} {} };   // most-derived constructs the virtual base

int main() {
    Player p;
    AudioSink* s = &p;
    Controllable* c = &p;
    s->write(128);
    c->pause();
    std::cout << "pointer adjusted? " << std::boolalpha
              << (static_cast<void*>(s) != static_cast<void*>(c)) << '\n';

    Duplex d;
    std::cout << "one shared Device, id=" << d.id << '\n';   // unambiguous thanks to virtual inheritance
}
