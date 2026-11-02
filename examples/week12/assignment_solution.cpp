#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <map>
#include <print>
#include <ranges>
#include <string>
#include <system_error>
#include <vector>

namespace fs = std::filesystem;

struct FileInfo { std::string rel; std::uintmax_t size; };

int main() {
    const fs::path root = fs::temp_directory_path() / "cpp_course_scan";
    std::error_code ec;
    fs::remove_all(root, ec);
    fs::create_directories(root / "album1");
    fs::create_directories(root / "album2");
    struct Make { const char* name; std::size_t size; };
    for (auto [name, size] : {Make{"album1/a.wav", 4000}, Make{"album1/b.flac", 2500}, Make{"album2/c.mp3", 900},
                              Make{"album2/d.wav", 6000}, Make{"album2/notes.txt", 100}}) {
        std::ofstream{root / name, std::ios::binary} << std::string(size, 'x');
    }

    std::map<std::string, int> per_ext;
    std::vector<FileInfo> files;
    std::uintmax_t total = 0;
    for (const auto& e : fs::recursive_directory_iterator(root, ec)) {
        if (!e.is_regular_file()) continue;
        auto ext = e.path().extension().string();
        if (ext != ".wav" && ext != ".flac" && ext != ".mp3") continue;
        ++per_ext[ext];
        files.push_back({fs::relative(e.path(), root).generic_string(), e.file_size()});
        total += e.file_size();
    }
    std::ranges::sort(files, [](const FileInfo& a, const FileInfo& b) { return a.size != b.size ? a.size > b.size : a.rel < b.rel; });

    std::println("{:<8}{:>6}", "ext", "count");
    for (const auto& [ext, n] : per_ext) std::println("{:<8}{:>6}", ext, n);
    std::println("total: {} files, {} bytes", files.size(), total);
    std::println("largest:");
    for (const auto& f : files | std::views::take(3)) std::println("  {:<16}{:>8}", f.rel, f.size);

    fs::remove_all(root, ec);
    std::println("cleanup ok: {}", !ec);
}
