/**
 * @file geometry_utils.hpp
 * @brief Geometric primitives and utility functions.
 *
 * Provides fundamental geometric structures and
 * operations used by convex hull algorithms.
 */

#ifndef CORE_GEOMETRY_UTILS_HPP
#define CORE_GEOMETRY_UTILS_HPP

#include <string>

/**
 * @brief Floating-point comparison tolerance.
 *
 * Used to compensate for numerical precision errors
 * during geometric computations.
 */
constexpr double EPSILON = 1e-12;

using namespace std;

/**
 * @brief Two-dimensional geometric point.
 *
 * Represents a labeled vertex used by computational
 * geometry algorithms.
 */
struct Vertex {
    string id;

    double x{0.0};
    double y{0.0};
};

/**
 * @brief Computes the orientation of three points.
 *
 * Calculates the signed cross product of vectors
 * OA and OB, where O is the origin point.
 *
 * Positive values indicate a counterclockwise turn,
 * negative values indicate a clockwise turn, and
 * zero indicates collinearity.
 *
 * @param origin
 * Common origin point.
 *
 * @param a
 * First endpoint.
 *
 * @param b
 * Second endpoint.
 *
 * @return double
 * Signed cross product value.
 */
double crossProduct(
    const Vertex& origin,
    const Vertex& a,
    const Vertex& b
);

/**
 * @brief Computes squared Euclidean distance.
 *
 * Returns the squared distance between two vertices.
 * The square root operation is intentionally avoided
 * to improve performance.
 *
 * @param a
 * First vertex.
 *
 * @param b
 * Second vertex.
 *
 * @return double
 * Squared Euclidean distance.
 */
double distanceSquared(
    const Vertex& a,
    const Vertex& b
);

/**
 * @brief Compares vertices lexicographically.
 *
 * Orders vertices according to their coordinates.
 * Used during preprocessing and sorting stages of
 * convex hull algorithms.
 *
 * @param a
 * First vertex.
 *
 * @param b
 * Second vertex.
 *
 * @return bool
 * True when a precedes b.
 */
bool compareVertices(
    const Vertex& a,
    const Vertex& b
);

/**
 * @brief Compares vertices by polar angle.
 *
 * Orders vertices according to their polar angle
 * relative to a pivot point. Collinear points are
 * ordered by distance from the pivot.
 *
 * @param pivot
 * Reference vertex.
 *
 * @param a
 * First vertex.
 *
 * @param b
 * Second vertex.
 *
 * @return bool
 * True when a precedes b in polar order.
 */
bool comparePolar(
    const Vertex& pivot,
    const Vertex& a,
    const Vertex& b
);

#endif // CORE_GEOMETRY_UTILS_HPP