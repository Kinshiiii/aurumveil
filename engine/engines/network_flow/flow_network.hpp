/**
 * @file flow_network.hpp
 * @brief Residual flow network data structures.
 *
 * Defines graph structures, edge representations,
 * and utility constants used by flow optimization
 * algorithms.
 */

#ifndef FLOW_NETWORK_HPP
#define FLOW_NETWORK_HPP

#include <vector>
#include <limits>

using namespace std;

/**
 * @brief Infinite distance sentinel value.
 *
 * Used to initialize shortest-path distances
 * before pathfinding algorithms are executed.
 */
constexpr int DISTANCE_INFINITY = numeric_limits<int>::max();

/**
 * @brief Invalid edge index sentinel.
 *
 * Represents a non-existing edge reference
 * during path reconstruction.
 */
constexpr size_t INVALID_EDGE = numeric_limits<size_t>::max();

/**
 * @brief Residual network edge.
 *
 * Represents a directed edge within the residual
 * flow network together with its reverse edge
 * reference.
 */
struct Edge {
    size_t destination;
    size_t reverseEdgeIndex;

    int capacity;
    int cost;
};

/**
 * @brief Residual flow network.
 *
 * Adjacency-list representation of a directed
 * residual graph used by flow optimization
 * algorithms.
 */
using FlowNetwork =
    vector<vector<Edge>>;

#endif //FLOW_NETWORK_HPP
