#ifndef CORE_GEOMETRY_HPP
#define CORE_GEOMETRY_HPP

#include <string>

using namespace std;

struct Point {
    string id;
    double x{0.0};
    double y{0.0};
};

constexpr double EPS = 1e-12;

double crossPoints(
    const Point& origin,
    const Point& a,
    const Point& b
);

double squaredDistance(
    const Point& a,
    const Point& b
);

bool comparePoints(
    const Point& a,
    const Point& b
);

bool polarComparator(
    const Point& pivot,
    const Point& a,
    const Point& b
);

#endif // CORE_GEOMETRY_HPP