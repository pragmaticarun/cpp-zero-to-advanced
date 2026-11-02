# Lesson 16.1: Interoperability: C, Python (pybind11), and Java/Android (JNI)

<span class="stdtag">C++20</span> · about 13 minutes

## Why this matters

Your C++ DSP engine is great — now the Python data team, the Android app and a legacy C codebase all want
it. The universal adapter is a **C API**: every language can call C. On top of it (or directly), tools like
pybind11 and JNI make C++ feel native in Python and Java.

## The opaque-handle pattern

Expose a C API with an incomplete type and create/destroy functions; never let C++ exceptions or types
cross the boundary:

```cpp title="examples/week16/lesson01.cpp"
--8<-- "examples/week16/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week16/lesson01.out"
```

Rules: catch everything at the boundary (`try { ... } catch (...) { return error_code; }`) — an exception
unwinding into C is undefined behaviour. Pass callbacks as a function pointer plus `void* user_data`.
Document who frees what.

## Python with pybind11

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;
PYBIND11_MODULE(dsp, m) {
    py::class_<Gain>(m, "Gain")
        .def(py::init<double>())
        .def("apply", &Gain::apply)
        .def_property_readonly("db", &Gain::db);
    m.def("rms", &rms, "Root mean square of a list of samples");
}
```

Build with CMake + `pybind11_add_module`, then `import dsp` in Python. pybind11 converts STL types and
translates exceptions to Python exceptions. **nanobind** is a lighter, faster successor. Release the GIL
(`py::gil_scoped_release`) around long C++ computations.

## Java/Android with JNI

```cpp
extern "C" JNIEXPORT jdouble JNICALL
Java_com_example_dsp_Native_rms(JNIEnv* env, jclass, jfloatArray samples) {
    jsize n = env->GetArrayLength(samples);
    jfloat* p = env->GetFloatArrayElements(samples, nullptr);
    double r = rms({p, static_cast<std::size_t>(n)});
    env->ReleaseFloatArrayElements(samples, p, JNI_ABORT);   // always release!
    return r;
}
```

On Android, the NDK builds C++ with CMake (`externalNativeBuild`) and you load it with
`System.loadLibrary("dsp")`. JNI local references, array pinning and thread attachment
(`AttachCurrentThread`) are the common traps.

## Key takeaways

!!! success "Key takeaways"
    - A C API with opaque handles is the universal interop layer.
    - Never let exceptions cross a C boundary; convert them to error codes.
    - pybind11/nanobind bind C++ to Python; JNI/NDK bind it to Java/Android.
    - Make ownership explicit across language boundaries.

## Quiz

**Q1.** Why must `dsp_mixer_process` catch all exceptions?

??? question "Show answer"
    Unwinding through C frames (or into another language's runtime) is undefined behaviour.

**Q2.** How does a C callback get access to the caller's state?

??? question "Show answer"
    Through a `void* user_data` parameter passed back to the callback.

**Q3.** What does `JNI_ABORT` in `ReleaseFloatArrayElements` mean?

??? question "Show answer"
    Free the buffer without copying changes back to the Java array (we only read it).

