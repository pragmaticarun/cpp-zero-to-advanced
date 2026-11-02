#include <cstdio>
#include <cstring>
#include <list>
#include <string>
#include <unordered_map>
#include <utility>

namespace cache {
class Lru {
public:
    explicit Lru(std::size_t cap) : cap_{cap} {}
    [[nodiscard]] const std::string* get(const std::string& k) {
        auto it = index_.find(k);
        if (it == index_.end()) return nullptr;
        order_.splice(order_.begin(), order_, it->second);
        return &it->second->second;
    }
    void put(std::string k, std::string v) {
        if (auto it = index_.find(k); it != index_.end()) { it->second->second = std::move(v); order_.splice(order_.begin(), order_, it->second); return; }
        if (order_.size() == cap_) { index_.erase(order_.back().first); order_.pop_back(); }
        order_.emplace_front(k, std::move(v));
        index_[std::move(k)] = order_.begin();
    }
    std::size_t size() const { return order_.size(); }
private:
    std::size_t cap_;
    std::list<std::pair<std::string, std::string>> order_;
    std::unordered_map<std::string, std::list<std::pair<std::string, std::string>>::iterator> index_;
};
}  // namespace cache

extern "C" {
typedef struct lru_cache lru_cache;
enum { LRU_OK = 0, LRU_MISS = 1, LRU_ERR = 2, LRU_TOO_SMALL = 3 };
lru_cache* lru_create(size_t capacity);
void lru_destroy(lru_cache* c);
int lru_put(lru_cache* c, const char* key, const char* value);
int lru_get(lru_cache* c, const char* key, char* out, size_t out_size);
}

struct lru_cache { cache::Lru impl; };

extern "C" lru_cache* lru_create(size_t capacity) {
    if (capacity == 0) return nullptr;
    try { return new lru_cache{cache::Lru{capacity}}; } catch (...) { return nullptr; }
}
extern "C" void lru_destroy(lru_cache* c) { delete c; }
extern "C" int lru_put(lru_cache* c, const char* key, const char* value) {
    if (!c || !key || !value) return LRU_ERR;
    try { c->impl.put(key, value); return LRU_OK; } catch (...) { return LRU_ERR; }
}
extern "C" int lru_get(lru_cache* c, const char* key, char* out, size_t out_size) {
    if (!c || !key || !out || out_size == 0) return LRU_ERR;
    try {
        const std::string* v = c->impl.get(key);
        if (!v) return LRU_MISS;
        if (v->size() + 1 > out_size) return LRU_TOO_SMALL;
        std::memcpy(out, v->c_str(), v->size() + 1);
        return LRU_OK;
    } catch (...) { return LRU_ERR; }
}

int main() {                                           // written like C client code
    lru_cache* c = lru_create(2);
    lru_put(c, "kick", "kick.wav");
    lru_put(c, "snare", "snare.wav");
    char buf[32];
    if (lru_get(c, "kick", buf, sizeof buf) == LRU_OK) std::printf("kick -> %s\n", buf);
    lru_put(c, "hat", "hat.wav");                       // evicts snare (least recently used)
    std::printf("snare -> %s\n", lru_get(c, "snare", buf, sizeof buf) == LRU_MISS ? "(evicted)" : buf);
    char tiny[4];
    std::printf("small buffer -> rc=%d\n", lru_get(c, "hat", tiny, sizeof tiny));
    std::printf("create(0) -> %s\n", lru_create(0) ? "handle" : "NULL");
    lru_destroy(c);
}
