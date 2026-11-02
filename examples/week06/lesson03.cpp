#include <iostream>
#include <memory>
#include <span>
#include <string>
#include <vector>

class AudioSink {                               // interface + NVI
public:
    virtual ~AudioSink() = default;
    AudioSink(const AudioSink&) = delete;       // prevent slicing copies
    AudioSink& operator=(const AudioSink&) = delete;

    void write(std::span<const float> buf) {     // non-virtual: common checks
        if (buf.empty()) return;
        ++writes_;
        do_write(buf);                           // customization point
    }
    int writes() const { return writes_; }
    virtual std::unique_ptr<AudioSink> clone() const = 0;   // polymorphic copy

protected:
    AudioSink() = default;
private:
    virtual void do_write(std::span<const float> buf) = 0;
    int writes_ = 0;
};

class ConsoleSink final : public AudioSink {
public:
    explicit ConsoleSink(std::string tag) : tag_{std::move(tag)} {}
    std::unique_ptr<AudioSink> clone() const override { return std::make_unique<ConsoleSink>(tag_ + "'"); }
private:
    void do_write(std::span<const float> buf) override {
        std::cout << tag_ << " got " << buf.size() << " samples\n";
    }
    std::string tag_;
};

class Probe {
public:
    virtual ~Probe() { std::cout << "~Probe\n"; }
};
class BigProbe : public Probe {
public:
    ~BigProbe() override { std::cout << "~BigProbe (members freed)\n"; }
    std::vector<int> data = std::vector<int>(1000);
};

int main() {
    std::unique_ptr<AudioSink> sink = std::make_unique<ConsoleSink>("speaker");
    const std::vector<float> buf(256);
    sink->write(buf);
    sink->write({});                             // ignored by the NVI wrapper
    auto copy = sink->clone();
    copy->write(buf);
    std::cout << "writes: " << sink->writes() << ' ' << copy->writes() << '\n';

    std::unique_ptr<Probe> p = std::make_unique<BigProbe>();
    p.reset();                                   // virtual dtor: both destructors run
}
