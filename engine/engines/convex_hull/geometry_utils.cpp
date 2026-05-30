#include <tuple>

#include "geometry_utils.hpp"

using namespace std;

bool compareVertices(const Vertex& a, const Vertex& b) {
    return tie(a.x, a.y) < tie(b.x, b.y);
}

double crossProduct(const Vertex& origin, const Vertex& a, const Vertex& b) {
    return (
        (a.x - origin.x) * (b.y - origin.y) -
        (a.y - origin.y) * (b.x - origin.x)
    );
}

double distanceSquared(const Vertex& a, const Vertex& b) {
    const double dx = a.x - b.x;
    const double dy = a.y - b.y;

    return dx * dx + dy * dy;
}

bool comparePolar(const Vertex& pivot, const Vertex& a, const Vertex& b) {
    const double cross =
        crossProduct(pivot, a, b);

    if (abs(cross) < EPSILON) {
        return
            distanceSquared(pivot, a) < distanceSquared(pivot, b);
    }

    return cross > 0;
}