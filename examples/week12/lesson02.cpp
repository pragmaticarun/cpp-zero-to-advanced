#include <iostream>
#include <memory>
#include <string>
#include <vector>

struct Buffer {
    std::string name;
    explicit Buffer(std::string n) : name{std::move(n)} {}
    ~Buffer() { std::cout << "  ~Buffer(" << name << ")\n"; }
};

struct Track;
struct Album {
    std::vector<std::shared_ptr<Track>> tracks;     // owns tracks
    ~Album() { std::cout << "  ~Album\n"; }
};
struct Track {
    std::weak_ptr<Album> album;                     // back-edge: observes, doesn't own
    ~Track() { std::cout << "  ~Track\n"; }
};

class Session : public std::enable_shared_from_this<Session> {
public:
    std::shared_ptr<Session> self() { return shared_from_this(); }
};

int main() {
    {
        auto buf = std::make_shared<Buffer>("pcm");
        auto view = buf;                            // second owner
        std::cout << "use_count=" << buf.use_count() << '\n';
        buf.reset();
        std::cout << "after reset, view still alive: " << view->name << '\n';
    }
    std::cout << "--- album with weak back-edges\n";
    {
        auto album = std::make_shared<Album>();
        auto t = std::make_shared<Track>();
        t->album = album;
        album->tracks.push_back(t);
        if (auto a = t->album.lock()) std::cout << "  track's album has " << a->tracks.size() << " track(s)\n";
    }                                               // everything freed: no cycle
    std::cout << "--- weak_ptr expiry\n";
    std::weak_ptr<Buffer> watcher;
    {
        auto b = std::make_shared<Buffer>("temp");
        watcher = b;
        std::cout << "  expired? " << std::boolalpha << watcher.expired() << '\n';
    }
    std::cout << "  expired? " << watcher.expired() << '\n';

    auto s = std::make_shared<Session>();
    auto s2 = s->self();
    std::cout << "session owners: " << s.use_count() << '\n';

    struct Pair { int a = 1; int b = 2; };
    auto p = std::make_shared<Pair>();
    std::shared_ptr<int> just_b(p, &p->b);          // aliasing: shares p's ownership
    p.reset();
    std::cout << "aliased member still valid: " << *just_b << '\n';
}
