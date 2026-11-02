#include <stdexcept>
int main() {
    int x = 1;
    throw std::runtime_error("boom");
    return x;
}
