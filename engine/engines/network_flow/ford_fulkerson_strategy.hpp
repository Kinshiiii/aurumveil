/**
 * @file ford_fulkerson_strategy.hpp
 * @brief Ford-Fulkerson maximum-flow strategy.
 *
 * Implements flow computation and residual network
 * augmentation according to the Ford-Fulkerson
 * method.
 */

#ifndef FORD_FULKERSON_STRATEGY_HPP
#define FORD_FULKERSON_STRATEGY_HPP

#include <algorithm>

#include "imaxflow_path_strategy.hpp"

using namespace std;

/**
 * @brief Ford-Fulkerson flow augmentation strategy.
 *
 * Computes augmenting flow values and updates the
 * residual network using the classical
 * Ford-Fulkerson approach.
 *
 * Complexity per augmentation:
 * O(L)
 *
 * where L is the length of the augmenting path.
 */
class FordFulkersonStrategy
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

        for (
            int vertex = sink;
            vertex != source;
            vertex = parentVertex[vertex]
        ) {
            const int previousVertex =
                parentVertex[vertex];

            Edge& currentEdge =
                graph[previousVertex]
                     [parentEdge[vertex]];

            pathFlow = min(
                pathFlow,
                currentEdge.capacity
            );
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
        for (
            int vertex = sink;
            vertex != source;
            vertex = parentVertex[vertex]
        ) {
            const int previousVertex =
                parentVertex[vertex];

            Edge& currentEdge =
                graph[previousVertex]
                     [parentEdge[vertex]];

            Edge& reverseEdge =
                graph[vertex]
                     [currentEdge.reverseEdgeIndex];

            currentEdge.capacity -= flow;
            reverseEdge.capacity += flow;

            totalCost +=
                flow * currentEdge.cost;
        }
    }
};

#endif // FORD_FULKERSON_STRATEGY_HPP