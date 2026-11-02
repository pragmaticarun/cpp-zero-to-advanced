#include <cstring>
#include <iostream>
#include <string>
#include <string_view>

using namespace std::literals;   // for "..."s and "..."sv

bool is_audio(std::string_view mime) { return mime.starts_with("audio/"); }

std::string_view extension(std::string_view path) {   // returns a view INTO path: caller keeps path alive
    const auto dot = path.rfind('.');
    return dot == std::string_view::npos ? std::string_view{} : path.substr(dot + 1);
}

int main() {
    const char* c = "hello";
    std::cout << "strlen=" << std::strlen(c) << " sizeof(\"hello\")=" << sizeof("hello") << '\n';

    std::string s = "track";
    s += "-01";                       // grows as needed
    s.insert(0, "my-");
    std::cout << s << " size=" << s.size() << '\n';

    std::cout << std::boolalpha << is_audio("audio/opus") << ' ' << is_audio(std::string{"video/h264"}) << '\n';

    const std::string path = "/sdcard/Music/song.flac";
    std::cout << "ext=" << extension(path) << '\n';

    auto owned = "literal"s;        // std::string
    auto view = "literal"sv;        // std::string_view
    std::cout << owned.size() << ' ' << view.size() << ' ' << (owned == view) << '\n';
    std::cout << "contains 'song'? " << path.contains("song") << '\n';   // C++23
}
