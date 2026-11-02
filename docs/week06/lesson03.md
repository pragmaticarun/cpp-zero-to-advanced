# Lesson 6.3: Abstract classes, interfaces, virtual destructors, and slicing

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

Two bugs show up in almost every codebase that uses inheritance. First: deleting a derived object through a
base pointer, and the derived destructor never runs — a leak. Second: copying a derived object into a base
*value*, and losing everything that made it derived. Both are easy to prevent once you've seen them. Let's
see them.

## Abstract classes and interfaces

A **pure virtual** function (`= 0`) has no implementation in the base; a class with one is **abstract** and
can't be instantiated. A class with only pure virtual functions (and a virtual destructor) is C++'s version
of an *interface*:

```cpp
class AudioSink {
public:
    virtual ~AudioSink() = default;
    virtual void write(std::span<const float>) = 0;
};
```

## Bug 1: no virtual destructor

```cpp
struct Base { ~Base() {} };                        // not virtual
struct Derived : Base { std::vector<int> big; };
Base* p = new Derived;
delete p;     // UB: only ~Base runs; Derived's members are never destroyed
```

**Rule:** a base class meant for polymorphic deletion needs a `public virtual` destructor. (If instead you
never delete through the base, make the base destructor `protected` and non-virtual — that prevents the
mistake at compile time.) `std::unique_ptr<Base>` relies on this too.

## Bug 2: slicing

```cpp
void log(Effect e);   // by value!
Gain g{2.0f};
log(g);               // copies only the Effect part: g is "sliced"; virtual calls see an Effect
```

Pass polymorphic objects by **reference or pointer**, never by value. To prevent slicing by accident,
delete the copy operations of polymorphic bases. If you need to copy a polymorphic object, add a virtual
`clone()`:

```cpp title="examples/week06/lesson03.cpp"
--8<-- "examples/week06/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week06/lesson03.out"
```

## The NVI idiom (non-virtual interface)

A useful design: the public function is non-virtual and does the common work (checks, logging, locking),
then calls a *private* virtual hook. Derived classes customize the hook but can't skip the checks. The
example's `write()` does this.

!!! tip "Pro tip"
    Enable `-Wnon-virtual-dtor` and `-Wdelete-non-virtual-dtor` (the latter is in `-Wall`). clang-tidy's
    `cppcoreguidelines-slicing` check catches slicing.

## Key takeaways

!!! success "Key takeaways"
    - A pure virtual function makes a class abstract; pure-virtual-only classes are interfaces.
    - Polymorphic bases need a public virtual destructor (or a protected non-virtual one).
    - Passing a derived object by value as a base slices it; pass by reference/pointer and delete base copies.
    - Use `clone()` for polymorphic copies and NVI to keep checks in non-virtual public functions.

## Quiz

**Q1.** What happens with `Base* p = new Derived; delete p;` if `~Base` isn't virtual?

??? question "Show answer"
    Undefined behaviour; in practice only `~Base` runs and the `Derived` part (its members) is never destroyed.

**Q2.** What is slicing?

??? question "Show answer"
    Copying a derived object into a base-class object, which copies only the base subobject; the derived data and overrides are lost.

**Q3.** Why make a polymorphic base's copy constructor deleted?

??? question "Show answer"
    To make accidental slicing copies (pass-by-value, assignment to a base object) compile errors.

