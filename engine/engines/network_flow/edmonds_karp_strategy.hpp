/**
 * @file edmonds_karp_strategy.hpp
 * @brief Edmonds-Karp maximum-flow strategy.
 *
 * Implements flow computation and residual network
 * augmentation according to the Edmonds-Karp
 * method.
 */

#ifndef EDMONDS_KARP_STRATEGY_HPP
#define EDMONDS_KARP_STRATEGY_HPP

#include <algorithm>

#include "imaxflow_path_strategy.hpp"

using namespace std;

/**
 * @brief Edmonds-Karp flow augmentation strategy.
 *
 * Computes augmenting flow values and updates the
 * residual network using paths discovered through
 * breadth-first search.
 *
 * Complexity per augmentation:
 * O(L)
 *
 * where L is the length of the augmenting path.
 */
class EdmondsKarpStrategy
    : public IMaxFlowStrategy
{
public:

    /**
     * @brief Computes bottleneck flow capacity.
     *
     * Traverses the augmenting path and determines
     * the minimum residual capacity available along
     * the route.
     *
     * @param graph
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
     * Maximum admissible augmenting flow.
     */
    int computeFlow(
        FlowNetwork& graph,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<size_t>& parentEdge
    ) override {
        constexpr int MAX_FLOW_LIMIT =
            1'000'000'000;

        int pathFlow =
            MAX_FLOW_LIMIT;

        int currentVertex =
            sink;

        while (currentVertex != source) {
            const int previousVertex =
                parentVertex[currentVertex];

            Edge& edge =
                graph[previousVertex]
                     [parentEdge[currentVertex]];

            pathFlow = min(
                pathFlow,
                edge.capacity
            );

            currentVertex =
                previousVertex;
        }

        return pathFlow;
    }

    /**
     * @brief Augments the residual network.
     *
     * Updates forward and reverse edge capacities
     * along the augmenting path and accumulates
     * the corresponding transportation cost.
     *
     * @param graph
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
    void augment(
        FlowNetwork& graph,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<size_t>& parentEdge,
        int flow,
        int& totalCost
    ) override {
        int currentVertex = sink;

        while (currentVertex != source) {
            const int previousVertex =
                parentVertex[currentVertex];

            Edge& edge =
                graph[previousVertex]
                     [parentEdge[currentVertex]];

            Edge& reverse =
                graph[currentVertex]
                     [edge.reverseEdgeIndex];

            edge.capacity -= flow;
            reverse.capacity += flow;

            totalCost +=
                flow * edge.cost;

            currentVertex =
                previousVertex;
        }
    }

    /**
     * @brief Calculates augmenting path length.
     *
     * Counts the number of edges forming the
     * reconstructed source-to-sink path.
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
     * Number of edges in the augmenting path.
     */
    int calculatePathLength(
        int source,
        int sink,
        const vector<int>& parentVertex
    ) override {
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
};

#endif // EDMONDS_KARP_STRATEGY_HPP