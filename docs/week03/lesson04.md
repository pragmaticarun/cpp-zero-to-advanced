# Lesson 3.4: Strings: C strings, std::string, and std::string_view

<span class="stdtag">C++23</span> · about 12 minutes

## Why this matters

Text is everywhere: file paths, log messages, codec names, JSON. C++ inherited C's strings — arrays of
`char` ending in a zero byte — and they've caused more security bugs than almost anything else. Modern
C++ gives you `std::string` to own text and `std::string_view` to look at it cheaply. Let's see when to
use which.

## C strings: an array and a promise

`"hello"` is an array of 6 `const char`s: `h e l l o \0`. Every C string function (`strlen`, `strcpy`,
`strcat`) walks until it finds that `\0`. If it's missing, or the destination buffer is too small,
you overflow memory. `strlen` is also O(n) every time you call it.

```cpp
char buf[8];
std::strcpy(buf, "much too long");   // WRONG: buffer overflow, UB
```

## `std::string`: owns its characters

`std::string` stores its length, grows as needed, and frees its memory automatically. Short strings
(typically up to 15 characters in libstdc++, 22 in libc++) are stored *inside* the string object with no
heap allocation: the **small string optimization** (SSO).

## `std::string_view`: a window onto characters (C++17)

A `string_view` is just a pointer + length. It doesn't own anything, never allocates, and can view a
`std::string`, a C string literal, or part of either. It's the ideal type for *read-only string
parameters*:

```cpp
bool is_audio(std::string_view mime) { return mime.starts_with("audio/"); }
is_audio("audio/opus");          // no std::string created
is_audio(some_std_string);       // no copy
```

```cpp title="examples/week03/lesson04.cpp"
--8<-- "examples/week03/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week03/lesson04.out"
```

## The big pitfall: string_view doesn't keep anything alive

```cpp
std::string_view codec_name() {
    std::string s = "opus";
    return s;                    // WRONG: view into a destroyed string
}
std::string_view v = std::string("tmp") + "x";   // WRONG: the temporary dies at the ';'
```

Rule: use `string_view` for parameters and short-lived local views; **return and store `std::string`**
unless you're returning a view into something that clearly outlives the caller (like a string literal or
a member).

!!! note "Also: a string_view isn't NUL-terminated"
    `sv.data()` isn't guaranteed to end in `\0`, so don't pass it to C functions expecting a C string.
    Convert with `std::string(sv).c_str()` when calling C APIs.

We'll cover text *formatting* (`std::format`, `std::print`) and the hard truth about Unicode in Week 12.

## Key takeaways

!!! success "Key takeaways"
    - C strings rely on a terminating `\0`; `strcpy`-style functions easily overflow.
    - `std::string` owns and manages text; short strings avoid heap allocation (SSO).
    - Take read-only text parameters as `std::string_view`.
    - Never return or store a `string_view` to something that may die first.

## Quiz

**Q1.** What is `sizeof("abc")`?

??? question "Show answer"
    4: three characters plus the terminating `\0`.

**Q2.** Why is `std::string_view` a good parameter type but a risky member/return type?

??? question "Show answer"
    As a parameter it avoids copies and accepts any string type, and the argument outlives the call. As a return/member it may outlive the characters it views, producing a dangling view.

**Q3.** Can you pass `sv.data()` to `fopen`?

??? question "Show answer"
    Not safely: a string_view's data isn't guaranteed to be NUL-terminated. Make a `std::string` first.

