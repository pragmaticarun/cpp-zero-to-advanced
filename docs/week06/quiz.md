# Week 6 quiz

Mixed review of the whole week. Try answering before you peek.

**Q1.** *(from 6.1)* In what order are these constructed: base `B`, members `m1`, `m2` of derived `D`, and `D`'s constructor body?

??? question "Show answer"
    `B`, then `m1`, then `m2` (declaration order), then the body of `D`'s constructor.

**Q2.** *(from 6.1)* What does `using Base::Base;` do?

??? question "Show answer"
    Inherits Base's constructors into the derived class (C++11).

**Q3.** *(from 6.2)* What does `override` buy you?

??? question "Show answer"
    A compile error if the function doesn't actually override a base virtual function (e.g. signature mismatch), instead of a silent new function.

**Q4.** *(from 6.2)* Why did `sizeof(WithVirtual)` grow?

??? question "Show answer"
    Objects of a polymorphic class carry a hidden vptr (8 bytes on 64-bit), plus padding for alignment.

**Q5.** *(from 6.3)* What happens with `Base* p = new Derived; delete p;` if `~Base` isn't virtual?

??? question "Show answer"
    Undefined behaviour; in practice only `~Base` runs and the `Derived` part (its members) is never destroyed.

**Q6.** *(from 6.3)* What is slicing?

??? question "Show answer"
    Copying a derived object into a base-class object, which copies only the base subobject; the derived data and overrides are lost.

**Q7.** *(from 6.4)* In a non-virtual diamond, how many `A` subobjects does `D` have?

??? question "Show answer"
    Two — one via `B` and one via `C`.

**Q8.** *(from 6.4)* With virtual inheritance, who calls the virtual base's constructor?

??? question "Show answer"
    The most-derived class. Initializers for the virtual base in intermediate classes are ignored when they aren't the most-derived.

**Q9.** *(from 6.5)* What does `dynamic_cast<D*>(p)` return if `*p` isn't a `D`?

??? question "Show answer"
    `nullptr`. (The reference form throws `std::bad_cast`.)

**Q10.** *(from 6.5)* Why shouldn't program logic depend on `typeid(x).name()`?

??? question "Show answer"
    Its contents are implementation-defined (and often mangled); they differ between compilers.

