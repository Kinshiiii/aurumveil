#ifndef CORE_CONVEX_HULL_HPP
#define CORE_CONVEX_HULL_HPP

#include <vector>

#include "geometry_utils.hpp"

using namespace std;

vector<Vertex> computeConvexHullJarvis(
    const vector<Vertex>& vertices
);

vector<Vertex> computeConvexHullGraham(
    vector<Vertex> vertices
);

vector<Vertex> computeConvexHullMonotoneChain(
    vector<Vertex> vertices
);

#endif // CORE_CONVEX_HULL_HPP