#ifndef CORE_GEOMETRY_UTILS_HPP
#define CORE_GEOMETRY_UTILS_HPP

#include <string>

constexpr double EPSILON = 1e-12;

using namespace std;

struct Vertex {
    string id;

    double x{0.0};
    double y{0.0};
};

double crossProduct(
    const Vertex& origin,
    const Vertex& a,
    const Vertex& b
);

double distanceSquared(
    const Vertex& a,
    const Vertex& b
);

bool compareVertices(
    const Vertex& a,
    const Vertex& b
);

bool comparePolar(
    const Vertex& pivot,
    const Vertex& a,
    const Vertex& b
);

#endif // CORE_GEOMETRY_UTILS_HPP