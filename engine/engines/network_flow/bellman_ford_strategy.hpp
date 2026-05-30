/**
 * @file bellman_ford_strategy.hpp
 * @brief Bellman-Ford shortest-path strategy.
 *
 * Implements a Bellman-Ford based shortest-path
 * algorithm for finding minimum-cost augmenting
 * paths in a residual flow network.
 */

#ifndef BELLMAN_FORD_STRATEGY_HPP
#define BELLMAN_FORD_STRATEGY_HPP

#include <queue>
#include <vector>

#include "ishortest_path_strategy.hpp"

using namespace std;

/**
 * @brief Bellman-Ford shortest-path strategy.
 *
 * Computes minimum-cost augmenting paths using
 * repeated edge relaxation and supports residual
 * networks containing negative-cost edges.
 *
 * This strategy is used during Minimum-Cost
 * Maximum-Flow optimization.
 */
class BellmanFordStrategy
    : public IShortestPathStrategy
{
public:

    /**
     * @brief Finds a minimum-cost augmenting path.
     *
     * Executes a Bellman-Ford style shortest-path
     * search on the residual network and stores
     * the resulting path reconstruction data.
     *
     * Negative-cost cycle detection is performed
     * using relaxation counters.
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
     * False when no path is available or a negative
     * cycle is detected.
     */
    bool findPath(
        FlowNetwork& graph,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<size_t>& parentEdge,
        vector<int>& distance
    ) override {

        const int vertexCount =
            static_cast<int>(
                graph.size()
            );

        distance.assign(
            vertexCount,
            DISTANCE_INFINITY
        );

        parentVertex.assign(
            vertexCount,
            -1
        );

        parentEdge.assign(
            graph.size(),
            INVALID_EDGE
        );

        vector<bool> isInQueue(
            vertexCount,
            false
        );

        vector<int> relaxationCount(
            vertexCount,
            0
        );

        queue<int> vertexQueue;

        distance[source] = 0;

        vertexQueue.push(
            source
        );

        isInQueue[source] = true;

        while (!vertexQueue.empty()) {
            const int currentVertex =
                vertexQueue.front();

            vertexQueue.pop();

            isInQueue[
                currentVertex
            ] = false;

            for (
                size_t edgeIndex = 0;
                edgeIndex < graph[currentVertex].size();
                ++edgeIndex
            ) {
                Edge& currentEdge =
                    graph[currentVertex]
                         [edgeIndex];

                const int destinationVertex =
                    static_cast<int>(
                        currentEdge
                            .destination
                    );

                if (currentEdge.capacity <= 0) {
                    continue;
                }

                if (distance[currentVertex] == DISTANCE_INFINITY) {
                    continue;
                }

                if (distance[destinationVertex] > distance[currentVertex] + currentEdge.cost) {
                    distance[
                        destinationVertex
                    ] =
                        distance[
                            currentVertex
                        ] + currentEdge.cost;

                    parentVertex[
                        destinationVertex
                    ] = currentVertex;

                    parentEdge[
                        destinationVertex
                    ] = edgeIndex;

                    ++relaxationCount[
                        destinationVertex
                    ];

                    if (relaxationCount[destinationVertex] > vertexCount) {
                        return false;
                    }

                    if (!isInQueue[destinationVertex]) {
                        vertexQueue.push(
                            destinationVertex
                        );

                        isInQueue[
                            destinationVertex
                        ] = true;
                    }
                }
            }
        }

        return distance[sink] != DISTANCE_INFINITY;
    }
};

#endif // BELLMAN_FORD_STRATEGY_HPP