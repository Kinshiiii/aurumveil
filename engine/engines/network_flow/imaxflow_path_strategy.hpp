/**
 * @file imaxflow_path_strategy.hpp
 * @brief Maximum-flow strategy interface.
 *
 * Defines the common interface implemented by all
 * maximum-flow algorithms used by the flow
 * optimization engine.
 */

#ifndef IMAXFLOW_PATH_STRATEGY_HPP
#define IMAXFLOW_PATH_STRATEGY_HPP

#include <vector>

#include "flow_network.hpp"

using namespace std;

/**
 * @brief Maximum-flow strategy interface.
 *
 * Provides a common abstraction for flow
 * augmentation algorithms used during
 * Minimum-Cost Maximum-Flow optimization.
 *
 * Implementations:
 * - FordFulkersonStrategy
 * - EdmondsKarpStrategy
 */
class IMaxFlowStrategy {
public:

    /**
     * @brief Computes an augmenting flow value.
     *
     * Determines the maximum admissible flow that
     * can be sent through the currently discovered
     * augmenting path.
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
     * Parent vertex table describing the path.
     *
     * @param parentEdge
     * Parent edge table describing the path.
     *
     * @return int
     * Augmenting flow value.
     */
    virtual int computeFlow(
        FlowNetwork& flowNetwork,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<size_t>& parentEdge
    ) = 0;

    /**
     * @brief Augments the residual network.
     *
     * Updates residual capacities along the
     * augmenting path and accumulates the
     * resulting transportation cost.
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
     * Parent vertex table describing the path.
     *
     * @param parentEdge
     * Parent edge table describing the path.
     *
     * @param flow
     * Flow value to augment.
     *
     * @param totalCost
     * Accumulated transportation cost.
     */
    virtual void augment(
        FlowNetwork& flowNetwork,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<size_t>& parentEdge,
        int flow,
        int& totalCost
    ) = 0;

    /**
     * @brief Calculates augmenting path length.
     *
     * Traverses the reconstructed path and returns
     * the number of edges between the source and sink.
     *
     * @param source
     * Source vertex.
     *
     * @param sink
     * Sink vertex.
     *
     * @param parentVertex
     * Parent vertex table describing the path.
     *
     * @return int
     * Number of edges forming the path.
     */
    virtual int calculatePathLength(
        int source,
        int sink,
        const vector<int>& parentVertex
    ) {
        int pathLength = 0;

        for (
            int vertex = sink;
            vertex != source;
            vertex = parentVertex[vertex]
        ) {
            ++pathLength;
        }

        return pathLength;
    }

    virtual ~IMaxFlowStrategy() = default;
};

#endif // IMAXFLOW_PATH_STRATEGY_HPP