/**
 * @file ishortest_path_strategy.hpp
 * @brief Shortest-path strategy interface.
 *
 * Defines the common interface implemented by all
 * shortest-path algorithms used by the flow
 * optimization engine.
 */

#ifndef ISHORTEST_PATH_STRATEGY_HPP
#define ISHORTEST_PATH_STRATEGY_HPP

#include <vector>

#include "flow_network.hpp"

using namespace std;

/**
 * @brief Shortest-path strategy interface.
 *
 * Provides a common abstraction for pathfinding
 * algorithms used during Minimum-Cost Maximum-Flow
 * optimization.
 */
class IShortestPathStrategy {
public:

    /**
     * @brief Searches for an augmenting path.
     *
     * Executes a shortest-path algorithm on the
     * residual flow network and stores the resulting
     * path information.
     *
     * @param flowNetwork
     * Residual flow network.
     *
     * @param source
     * Source vertex.
     *
     * @param sink
     * Sink vertex.
     *
     * @param parentVertex
     * Parent vertex table used for path reconstruction.
     *
     * @param parentEdge
     * Parent edge table used for path reconstruction.
     *
     * @param distance
     * Computed shortest-path distances.
     *
     * @return bool
     * True when a valid augmenting path exists.
     */
    virtual bool findPath(
        FlowNetwork& flowNetwork,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<size_t>& parentEdge,
        vector<int>& distance
    ) = 0;

    virtual ~IShortestPathStrategy() = default;
};

#endif // ISHORTEST_PATH_STRATEGY_HPP