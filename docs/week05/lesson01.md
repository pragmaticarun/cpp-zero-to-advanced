# Lesson 5.1: Copy semantics and the Rule of Three

<span class="stdtag">C++20</span> · about 11 minutes

## Why this matters

Write a class that owns a heap buffer with a raw pointer, copy it once, and your program will crash at exit
with a double free. Why? The compiler-generated copy just copies the *pointer*, so two objects think they own
the same buffer. Understanding exactly what "copy" means for your class is the foundation for everything
this week.

## The six special member functions

For every class, the compiler can generate: default constructor, destructor, copy constructor, copy
assignment, move constructor, move assignment. The generated copy operations copy **each member**.
For an `int` or `std::string` member, that's perfect. For a raw owning pointer, it's a disaster.

## The wrong way: shallow copy of an owning pointer

```cpp
class Buffer {
    float* data_; std::size_t n_;
public:
    explicit Buffer(std::size_t n) : data_{new float[n]{}}, n_{n} {}
    ~Buffer() { delete[] data_; }
    // no copy operations written: compiler copies the pointer
};
Buffer a{1024};
Buffer b = a;    // b.data_ == a.data_  -> both destructors delete[] it -> double free (UB)
```

## The Rule of Three

> If a class needs a user-written destructor, copy constructor, or copy assignment operator, it almost
> certainly needs all three.

Because a custom destructor means "I manage a resource", and then copying must decide what happens to that
resource: **deep copy** (duplicate it), **forbid copying** (`= delete`), or **share it** (reference count).

## A correct deep copy, with copy-and-swap

```cpp title="examples/week05/lesson01.cpp"
--8<-- "examples/week05/lesson01.cpp"
```

**Output**:

```text
--8<-- "examples/week05/lesson01.out"
```

The **copy-and-swap** idiom for assignment: take the parameter *by value* (that makes the copy), then swap
our contents with it. The old contents get destroyed with the parameter. It's automatically safe for
self-assignment (`a = a`) and gives the strong exception guarantee (Week 9): if the copy throws, `*this`
is untouched. It's not always the fastest, but it's very hard to get wrong.

!!! tip "Pro tip: the best Rule of Three is no rule at all"
    If `Buffer` held a `std::vector<float>` instead of a raw pointer, you'd write *none* of these functions
    and copying would just work. That's the Rule of Zero, coming in Lesson 5.3.

## Key takeaways

!!! success "Key takeaways"
    - Compiler-generated copies copy each member; for raw owning pointers that means double frees.
    - Rule of Three: a custom destructor, copy ctor or copy assignment usually means you need all three.
    - Copy-and-swap gives safe, exception-safe assignment with little code.
    - Better still: hold resources in members that already copy correctly (Rule of Zero).

## Quiz

**Q1.** What does the implicitly generated copy constructor do?

??? question "Show answer"
    Copy-constructs each base and member in declaration order (memberwise copy).

**Q2.** Why is copy-and-swap safe for self-assignment?

??? question "Show answer"
    The parameter is a full copy made before anything in `*this` changes, so swapping with it is fine even if the source was `*this`.

**Q3.** Your class has a `std::FILE*` it closes in the destructor. What are your options for copying?

??? question "Show answer"
    Delete copying (most common), implement a deep copy (open another handle — rarely meaningful), or share ownership with reference counting (e.g. `std::shared_ptr` with a deleter).

