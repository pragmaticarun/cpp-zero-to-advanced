# Lesson 15.1: Build systems: CMake, packages, and C++20 modules

<span class="stdtag">C++20</span> · about 13 minutes

## Why this matters

Your project grows from one file to fifty, plus three libraries. Compiling by hand stops scaling the first
day. CMake is the de facto standard C++ build generator, and C++20 modules are the first real fix for
C++'s 50-year-old textual `#include` model, which re-parses the same headers thousands of times.

## Modern CMake: think in targets

```cmake
cmake_minimum_required(VERSION 3.28)
project(mixer LANGUAGES CXX)

add_library(dsp src/gain.cpp src/filter.cpp)
target_include_directories(dsp PUBLIC include)
target_compile_features(dsp PUBLIC cxx_std_20)
target_compile_options(dsp PRIVATE -Wall -Wextra -Wpedantic)

add_executable(mixer src/main.cpp)
target_link_libraries(mixer PRIVATE dsp)

include(FetchContent)
FetchContent_Declare(Catch2 GIT_REPOSITORY https://github.com/catchorg/Catch2.git GIT_TAG v3.5.2)
FetchContent_MakeAvailable(Catch2)
add_executable(tests tests/test_gain.cpp)
target_link_libraries(tests PRIVATE dsp Catch2::Catch2WithMain)
enable_testing()
add_test(NAME tests COMMAND tests)
```

`PUBLIC`/`PRIVATE`/`INTERFACE` say whether a usage requirement propagates to dependents. Avoid global
`include_directories` / `CMAKE_CXX_FLAGS` — set properties on targets. Build out of source:
`cmake -S . -B build -G Ninja && cmake --build build && ctest --test-dir build`.

## Modules (C++20)

```cpp
// gain.cppm
export module dsp.gain;
export double apply_gain(double x, double g) { return x * g; }
// main.cpp
import dsp.gain;
import std;            // C++23: the whole standard library as one module
```

Modules are compiled once into a binary interface, don't leak macros, and make the interface explicit
(`export`). Honest status (2026): MSVC, Clang ≥ 17 and GCC ≥ 14 support them, and CMake ≥ 3.28 handles
dependency scanning with Ninja — but tooling (IDEs, package managers) is still catching up, so many
codebases still use headers. Our checker compiles single files, so modules are shown here, not compiled.

## Portable feature detection

When code must work across compilers, test feature-test macros rather than compiler versions:

```cpp title="examples/week15/lesson01.cpp"
--8<-- "examples/week15/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week15/lesson01.out"
```

## Key takeaways

!!! success "Key takeaways"
    - Modern CMake is target-based: set includes, features and links on targets with PUBLIC/PRIVATE.
    - Use FetchContent or a package manager (vcpkg, Conan) for dependencies.
    - Modules replace textual inclusion with compiled interfaces; tooling support is maturing.
    - Use `<version>` feature-test macros for portability, not compiler-version checks.

## Quiz

**Q1.** What does `PUBLIC` mean in `target_include_directories(dsp PUBLIC include)`?

??? question "Show answer"
    The include directory is used to build `dsp` *and* propagates to targets that link `dsp`.

**Q2.** Name two advantages of modules over headers.

??? question "Show answer"
    Faster builds (parsed once), no macro leakage, explicit export control, less ODR fragility.

**Q3.** Why prefer `#ifdef __cpp_lib_expected` over checking GCC's version?

??? question "Show answer"
    It checks the actual feature, works across compilers and standard libraries, and handles `-std` modes.

