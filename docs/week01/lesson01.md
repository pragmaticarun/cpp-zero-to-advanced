# Lesson 1.1: Hello, toolchain: compilers, CMake and Compiler Explorer

<span class="stdtag">C++20</span> · about 10 minutes

## Why this matters

Before we can learn a language, we need a way to *run* it. In Python you type `python file.py` and
you're done. C++ is different: it is a **compiled** language, so a tool called a *compiler* turns your
text into machine code ahead of time. That's a big part of why C++ is fast — and also why there are a
few more moving parts. Let's set those up once, properly, so they never get in your way again.

## Your first program

Let's start with the smallest useful C++ program.

```cpp title="examples/week01/lesson01.cpp"
--8<-- "examples/week01/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week01/lesson01.out"
```

Let's go through it line by line:

- `#include <iostream>` pulls in the declarations for input/output streams. (We'll see exactly what
  "pulls in" means in the next lesson.)
- `int main()` is where every hosted C++ program starts. It returns an `int` to the operating system:
  `0` means success.
- `std::cout << "..."` writes text to standard output. `std::` means "from the standard library namespace".
- `'\n'` is a newline character.

## Compiling it by hand

On Linux or macOS, with GCC or Clang installed:

```bash
g++ -std=c++20 -Wall -Wextra -Wpedantic hello.cpp -o hello
./hello
```

Each flag matters:

| Flag | What it does |
|---|---|
| `-std=c++20` | Which version of the language to use. C++ evolves every 3 years: 11, 14, 17, 20, 23, 26. |
| `-Wall -Wextra` | Turn on lots of useful warnings. Despite the name, `-Wall` is *not* all of them. |
| `-Wpedantic` | Warn about non-standard compiler extensions. |
| `-o hello` | Name the output file. |

!!! tip "Pro tip: treat warnings as bugs"
    A warning is the compiler saying "this is legal, but you probably didn't mean it."
    In this course every example compiles **warning-free** with these flags; that's checked
    automatically. On real projects, add `-Werror` in CI so warnings can't creep in.

`clang++` accepts the same flags. On Windows, MSVC uses `/std:c++20 /W4`. Throughout the course
we test with both GCC and Clang.

## Compiler Explorer: your new best friend

[Compiler Explorer](https://godbolt.org) lets you paste code and instantly see the assembly produced by
dozens of compilers. You don't need to read assembly fluently. But when we talk about "zero-cost
abstractions" later, you'll be able to *see* that the abstraction really did disappear. Bookmark it.

## CMake: building more than one file

For anything beyond one file, you'll want a build system. The de-facto standard is **CMake**. A minimal
`CMakeLists.txt` looks like this:

```cmake
cmake_minimum_required(VERSION 3.20)
project(hello LANGUAGES CXX)

add_executable(hello hello.cpp)
target_compile_features(hello PRIVATE cxx_std_20)
target_compile_options(hello PRIVATE -Wall -Wextra -Wpedantic)
```

And you build it with:

```bash
cmake -S . -B build        # configure: generate build files into ./build
cmake --build build        # build
./build/hello
```

Notice the pattern: **targets** (here `hello`) and properties attached to targets. That's "modern CMake",
and we'll go much deeper in Week 15. Coming from Android? Good news: the NDK uses exactly this
CMake, so this skill transfers directly.

## A slightly bigger example

Here's a program that reads from the user. Don't worry about every detail yet.

```cpp title="examples/week01/lesson01_input.cpp"
--8<-- "examples/week01/lesson01_input.cpp"
```

**Output**:

```text
--8<-- "examples/week01/lesson01_input.out"
```

When there's no input (as in our automated test run), `std::cin >> name` fails, and we fall back
to a default. Checking whether input succeeded is a habit worth building on day one.

## Key takeaways

!!! success "Key takeaways"
    - C++ is compiled ahead of time; the compiler turns source text into a native executable.
    - Always compile with a fixed standard and warnings on: `-std=c++20 -Wall -Wextra -Wpedantic`.
    - Compiler Explorer shows you what the compiler generates — use it to build intuition.
    - CMake describes *targets* and their properties; the NDK uses the same CMake.

## Quiz

**Q1.** What does `return 0;` from `main` mean?

??? question "Show answer"
    It reports success to the operating system. Non-zero means failure. In `main` (and only `main`) you may omit it, and it behaves as `return 0;`.

**Q2.** Does `-Wall` enable all warnings?

??? question "Show answer"
    No. Despite its name it enables a common set. `-Wextra` adds more, and there are still others (like `-Wconversion`) that you turn on separately.

**Q3.** In CMake, what is a *target*?

??? question "Show answer"
    Something the build produces (an executable or library) that properties like compile features, options and include paths are attached to, e.g. `add_executable(hello ...)` creates target `hello`.

## Practice lab (optional)

Write a program that asks for two integers and prints their sum and product. If reading fails,
print `invalid input` and return `1`. Build it once by hand with `g++` and once with CMake.

???+ example "Starter code"
    ```cpp title="examples/week01/lesson01_lab_starter.cpp"
    --8<-- "examples/week01/lesson01_lab_starter.cpp"
    ```

??? tip "Full solution"
    ```cpp title="examples/week01/lesson01_lab_solution.cpp"
    --8<-- "examples/week01/lesson01_lab_solution.cpp"
    ```

