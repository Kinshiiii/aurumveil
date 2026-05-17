#ifndef CORE_CONVEX_HULL_HPP
#define CORE_CONVEX_HULL_HPP

#include <vector>

#include "geometry.hpp"

using namespace std;

vector<Point> computeConvexHullJarvis(
    const vector<Point>& points
);

vector<Point> computeConvexHullGraham(
    vector<Point> points
);

vector<Point> computeConvexHullMonotoneChain(
    vector<Point> points
);

#endif // CORE_CONVEX_HULL_HPP