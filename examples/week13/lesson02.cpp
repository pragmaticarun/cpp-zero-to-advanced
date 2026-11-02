#include <iostream>
#include <map>
#include <mutex>
#include <shared_mutex>
#include <string>
#include <thread>
#include <vector>

struct Account { std::mutex m; int balance; };

void transfer(Account& from, Account& to, int amount) {
    std::scoped_lock lock{from.m, to.m};       // locks both, deadlock-free regardless of order
    from.balance -= amount;
    to.balance += amount;
}

class Settings {
public:
    std::string get(const std::string& k) const {
        std::shared_lock lock{m_};             // many readers at once
        auto it = values_.find(k);
        return it == values_.end() ? "" : it->second;
    }
    void set(const std::string& k, std::string v) {
        std::unique_lock lock{m_};             // exclusive writer
        values_[k] = std::move(v);
    }
private:
    mutable std::shared_mutex m_;
    std::map<std::string, std::string> values_;
};

int main() {
    int counter = 0;
    std::mutex m;
    {
        std::vector<std::jthread> ts;
        for (int t = 0; t < 4; ++t)
            ts.emplace_back([&] { for (int i = 0; i < 100000; ++i) { std::lock_guard lock{m}; ++counter; } });
    }
    std::cout << "counter = " << counter << '\n';

    Account a{{}, 1000}, b{{}, 1000};
    {
        std::jthread t1{[&] { for (int i = 0; i < 1000; ++i) transfer(a, b, 1); }};
        std::jthread t2{[&] { for (int i = 0; i < 1000; ++i) transfer(b, a, 1); }};   // opposite order: no deadlock
    }
    std::cout << "balances " << a.balance << ' ' << b.balance << '\n';

    Settings s;
    s.set("rate", "48000");
    {
        std::vector<std::jthread> readers;
        for (int i = 0; i < 3; ++i) readers.emplace_back([&] { for (int j = 0; j < 1000; ++j) (void)s.get("rate"); });
        s.set("bits", "24");
    }
    std::cout << "rate=" << s.get("rate") << " bits=" << s.get("bits") << '\n';

    std::once_flag once;
    int inits = 0;
    {
        std::vector<std::jthread> ts;
        for (int i = 0; i < 4; ++i) ts.emplace_back([&] { std::call_once(once, [&] { ++inits; }); });
    }
    std::cout << "initialized " << inits << " time(s)\n";
}
