// Wrong way: `override` catches a signature mismatch (missing const).
struct Base { virtual ~Base() = default; virtual void draw() const {} };
struct Oops : Base { void draw() override {} };   // error: does not override
int main() {}
