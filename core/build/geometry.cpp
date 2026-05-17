#include "geometry.hpp"

#include <tuple>

using namespace std;

bool comparePoints(const Point& a, const Point& b) {
    return tie(a.x, a.y) < tie(b.x, b.y);
}

double crossPoints(const Point& origin, const Point& a, const Point& b) {
    return (a.x - origin.x) * (b.y - origin.y) - (a.y - origin.y) * (b.x - origin.x);
}

double squaredDistance(const Point& a, const Point& b) {
    const double dx = a.x - b.x;
    const double dy = a.y - b.y;

    return dx * dx + dy * dy;
}

bool polarComparator(const Point& pivot, const Point& a, const Point& b) {
    double cross = crossPoints(
        pivot,
        a,
        b
    );

    if (abs(cross) < EPS) {
        return squaredDistance(pivot, a) < squaredDistance(pivot, b);
    }

    return cross > 0;
}