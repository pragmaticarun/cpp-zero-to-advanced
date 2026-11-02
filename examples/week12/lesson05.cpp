#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <system_error>
#include <vector>

namespace fs = std::filesystem;

int main() {
    const fs::path root = fs::temp_directory_path() / "cpp_course_fs_demo";
    fs::remove_all(root);                                          // start clean
    fs::create_directories(root / "presets" / "drums");

    for (const char* name : {"presets/kick.json", "presets/drums/snare.json", "presets/readme.txt"}) {
        std::ofstream out{root / name, std::ios::binary};
        out << "{\"name\": \"" << fs::path{name}.stem().string() << "\"}";
    }

    fs::path p = root / "presets" / "kick.json";
    std::cout << "filename=" << p.filename() << " stem=" << p.stem() << " ext=" << p.extension() << '\n';
    std::cout << "as flac: " << fs::path{p}.replace_extension(".flac").filename() << '\n';

    std::vector<std::string> found;
    for (const auto& entry : fs::recursive_directory_iterator(root))
        if (entry.is_regular_file() && entry.path().extension() == ".json")
            found.push_back(fs::relative(entry.path(), root).generic_string());
    std::ranges::sort(found);                                       // iteration order is unspecified
    for (const auto& f : found) std::cout << "json: " << f << '\n';

    std::ifstream in{p, std::ios::binary};
    std::string content{std::istreambuf_iterator<char>{in}, {}};
    std::cout << "content: " << content << " (" << fs::file_size(p) << " bytes)\n";

    std::error_code ec;
    fs::remove(root / "does-not-exist.txt", ec);                    // no TOCTOU, no exception
    std::cout << "remove missing file -> error? " << std::boolalpha << static_cast<bool>(ec) << '\n';
    fs::rename(root / "presets" / "readme.txt", root / "README.txt");
    std::cout << "renamed exists: " << fs::exists(root / "README.txt") << '\n';
    std::cout << "removed " << fs::remove_all(root) << " entries\n";
}
