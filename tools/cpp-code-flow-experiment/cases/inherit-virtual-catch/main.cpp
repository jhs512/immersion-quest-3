#include <cstdio>
#include <stdexcept>
#include <vector>

struct Shape {
    int id;
    explicit Shape(int i) : id(i) {}
    virtual ~Shape() {}
    virtual int area() const { return 0; }
};

struct Square : Shape {
    int side;
    Square(int i, int s) : Shape(i), side(s) {}
    int area() const override { return side * side; }
};

int total(const std::vector<Shape*> &shapes) {
    int sum = 0;
    for (const Shape *s : shapes) {
        sum += s->area();
    }
    return sum;
}

int check(int v) {
    if (v < 0) {
        throw std::invalid_argument("negative");
    }
    return v;
}

int main() {
    Square sq(1, 3);
    Shape base(2);
    std::vector<Shape*> shapes = {&sq, &base};
    int t = total(shapes);
    int r = 0;
    try {
        r = check(-1);
    } catch (const std::invalid_argument &e) {
        std::printf("caught %s\n", e.what());
    }
    std::printf("%d %d\n", t, r);
    return 0;
}
