# Setup

You need a C++20 compiler (C++23 for a few lessons), CMake, and an editor.

=== "Linux (Debian/Ubuntu)"
    ```bash
    sudo apt install g++-14 clang cmake ninja-build gdb
    g++-14 --version
    ```
=== "macOS"
    ```bash
    xcode-select --install        # Apple clang
    brew install llvm cmake ninja # newer clang with more C++23 support
    ```
=== "Windows"
    Install **Visual Studio 2022** (Desktop development with C++), or use WSL2 with the Linux instructions.

**Recommended editors:** VS Code with the *clangd* extension, CLion, or Visual Studio.

## Compiler support

C++20 is well supported by GCC ≥ 13, Clang ≥ 17 and MSVC 19.3x. C++23 library features vary:
`std::print`, `std::expected` work in GCC 14 and recent Clang/libc++; `std::flat_map` needs GCC 15 or
libc++ 20+; `std::generator` is in GCC 14 but not yet in libc++. Lessons tell you when a feature needs a
recent compiler. Check [cppreference's compiler support table](https://en.cppreference.com/w/cpp/compiler_support).

## Get the examples

```bash
git clone https://github.com/pragmaticarun/cpp-zero-to-advanced
cd cpp-zero-to-advanced
scripts/check_examples.sh          # compile & run everything
CXX=clang++ scripts/check_examples.sh week03   # just one week, another compiler
```
