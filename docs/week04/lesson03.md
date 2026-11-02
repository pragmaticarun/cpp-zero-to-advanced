# Lesson 4.3: RAII: tying resources to object lifetime

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

Suppose you open a file, lock a mutex, or grab a hardware codec. Then something goes wrong halfway
through — an early `return`, an exception. Who releases the resource? In C you write `goto cleanup` and
hope you covered every path. In C++ the answer is beautiful: *the destructor does*, automatically, on every
path. This idea is called RAII, and it's the most important idiom in C++.

## The wrong way: manual cleanup

```cpp
bool save(const char* path, const Data& d) {
    std::FILE* f = std::fopen(path, "wb");
    if (!f) return false;
    if (!write_header(f, d)) return false;       // LEAK: forgot fclose
    write_body(f, d);                            // if this throws: LEAK
    std::fclose(f);
    return true;
}
```

Every new exit path is a chance to forget cleanup.

## RAII: acquire in the constructor, release in the destructor

The trick is to wrap the resource in a small class whose destructor releases it. Because destructors of
local objects run whenever a scope is left — normal flow, `return`, `break`, or an exception unwinding
the stack — cleanup happens on *every* path, with no extra code at the call site.

```cpp title="examples/week04/lesson03.cpp"
--8<-- "examples/week04/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week04/lesson03.out"
```

Look at the output: when the exception propagates out of `process`, the `File` destructor still runs
before the `catch` block. That's **stack unwinding**.

A few design points in that `File` class:

- The copy operations are `= delete`d. Two `File` objects owning the same `FILE*` would both call
  `fclose` — a double close. (In Week 5 we'll make it *movable* so ownership can be transferred.)
- The constructor throws if it can't acquire the resource. That way, a `File` object that exists is always
  a valid, open file: a class invariant.

## RAII is everywhere in the standard library

| Resource | RAII type |
|---|---|
| heap memory | `std::vector`, `std::string`, `std::unique_ptr`, `std::shared_ptr` |
| mutex lock | `std::lock_guard`, `std::scoped_lock`, `std::unique_lock` |
| thread | `std::jthread` (joins in its destructor) |
| file | `std::fstream` |

You can also make a general **scope guard** — an object that runs a lambda in its destructor — for one-off
cleanup actions. The example includes a tiny one.

!!! tip "Pro tip: Android & C APIs"
    NDK APIs are C APIs: `AMediaCodec_delete`, `AAsset_close`, `ANativeWindow_release`... Wrap each in an
    RAII type (or `std::unique_ptr` with a custom deleter, Week 12) once, and your JNI code stops leaking.

## Key takeaways

!!! success "Key takeaways"
    - RAII: acquire a resource in a constructor, release it in the destructor.
    - Destructors run on every exit path, including exceptions (stack unwinding).
    - A resource-owning class must decide its copy behaviour; often `= delete` copies (and allow moves).
    - The standard library is RAII all the way down; wrap C handles the same way.

## Quiz

**Q1.** Why does RAII make code exception-safe without try/catch at every call site?

??? question "Show answer"
    Destructors of local objects run during stack unwinding, so resources are released whatever path leaves the scope.

**Q2.** What goes wrong if a `File` RAII class is copyable with the default copy constructor?

??? question "Show answer"
    Both copies hold the same `FILE*` and both destructors call `fclose` on it — a double close (UB).

**Q3.** Name three RAII types from the standard library.

??? question "Show answer"
    For example `std::vector`, `std::unique_ptr`, `std::lock_guard`, `std::jthread`, `std::fstream`.

## Practice lab (optional)

Write an RAII class `Timer` that records `std::chrono::steady_clock::now()` in its constructor and prints the
elapsed milliseconds (with a label) in its destructor. Use it to time a loop. Make it non-copyable.

??? tip "Full solution"
    ```cpp title="examples/week04/lesson03_lab_solution.cpp"
    --8<-- "examples/week04/lesson03_lab_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week04/lesson03_lab_solution.out"
    ```

