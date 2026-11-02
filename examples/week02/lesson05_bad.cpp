// Wrong way: scoped enums don't convert implicitly to int.
enum class Codec { aac, opus };
int main() {
    int n = Codec::opus;   // error: cannot convert 'Codec' to 'int'
    return n;
}
