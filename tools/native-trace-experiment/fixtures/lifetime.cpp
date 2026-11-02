#include <iostream>
#include <memory>
#include <string>
#include <vector>

struct Box {
    int value;
    Box(int v) : value(v) { std::cout << "make " << value << "\n"; }
    ~Box() { std::cout << "drop " << value << "\n"; }
};

int twice(const int &n) {
    return n * 2;
}

int main() {
    int stock = 2;
    int &alias = stock;
    alias = twice(stock);
    std::vector<int> values = {1, 2, 3};
    values.push_back(stock);
    std::string name = "pen";
    auto owned = std::make_unique<Box>(7);
    Box *raw = new Box(9);
    {
        Box local(5);
        stock += local.value;
    }
    delete raw;
    long double wide = 1.5L;
    unsigned long long big = 18446744073709551615ULL;
    std::cout << stock << " " << values.size() << " " << name << " " << owned->value << " " << big << " " << (double)wide << "\n";
    return 0;
}
