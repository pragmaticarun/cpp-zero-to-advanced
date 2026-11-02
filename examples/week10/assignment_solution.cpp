#include <cstddef>
#include <iostream>
#include <list>
#include <optional>
#include <string>
#include <unordered_map>
#include <utility>

template <typename Key, typename Value>
class LruCache {
public:
    explicit LruCache(std::size_t cap) : cap_{cap} {}
    std::optional<Value> get(const Key& k) {
        auto it = index_.find(k);
        if (it == index_.end()) return std::nullopt;
        order_.splice(order_.begin(), order_, it->second);     // O(1) move to front
        return it->second->second;
    }
    void put(Key k, Value v) {
        if (auto it = index_.find(k); it != index_.end()) {
            it->second->second = std::move(v);
            order_.splice(order_.begin(), order_, it->second);
            return;
        }
        if (order_.size() == cap_) {
            std::cout << "  evict " << order_.back().first << '\n';
            index_.erase(order_.back().first);
            order_.pop_back();
        }
        order_.emplace_front(k, std::move(v));
        index_[std::move(k)] = order_.begin();
    }
private:
    std::size_t cap_;
    std::list<std::pair<Key, Value>> order_;
    std::unordered_map<Key, typename std::list<std::pair<Key, Value>>::iterator> index_;
};

int main() {
    LruCache<std::string, int> c{2};
    c.put("kick", 1);
    c.put("snare", 2);
    std::cout << "get kick: " << c.get("kick").value_or(-1) << '\n';
    c.put("hat", 3);                     // evicts snare (least recently used)
    std::cout << "get snare: " << c.get("snare").value_or(-1) << '\n';
    std::cout << "get hat: " << c.get("hat").value_or(-1) << '\n';
}
