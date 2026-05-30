/**
 * @file convex_hull.hpp
 * @brief Convex hull algorithm interfaces.
 *
 * Declares convex hull algorithms used to determine
 * the protected boundary of the dwarven kingdom.
 */

#ifndef CORE_CONVEX_HULL_HPP
#define CORE_CONVEX_HULL_HPP

#include <vector>

#include "geometry_utils.hpp"

using namespace std;

/**
 * @brief Computes a convex hull using Jarvis March.
 *
 * Constructs the convex hull by iteratively selecting
 * the next boundary vertex with the smallest turning
 * angle relative to the current hull edge.
 *
 * @param vertices
 * Input point set.
 *
 * @return vector<Vertex>
 * Convex hull vertices in traversal order.
 */
vector<Vertex> computeConvexHullJarvis(
    const vector<Vertex>& vertices
);

/**
 * @brief Computes a convex hull using Graham Scan.
 *
 * Sorts vertices by polar angle and incrementally
 * constructs the convex hull using a stack-based
 * approach.
 *
 * @param vertices
 * Input point set.
 *
 * @return vector<Vertex>
 * Convex hull vertices in traversal order.
 */
vector<Vertex> computeConvexHullGraham(
    vector<Vertex> vertices
);

/**
 * @brief Computes a convex hull using Monotone Chain.
 *
 * Constructs lower and upper hulls independently
 * and combines them into a complete convex boundary.
 *
 * @param vertices
 * Input point set.
 *
 * @return vector<Vertex>
 * Convex hull vertices in traversal order.
 */
vector<Vertex> computeConvexHullMonotoneChain(
    vector<Vertex> vertices
);

#endif // CORE_CONVEX_HULL_HPP