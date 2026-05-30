/**
 * @file desopo_pape_strategy.hpp
 * @brief D'Esopo-Pape shortest-path strategy.
 *
 * Implements the D'Esopo-Pape algorithm for finding
 * minimum-cost augmenting paths in a residual flow
 * network.
 */

#ifndef DESOPO_PAPE_STRATEGY_HPP
#define DESOPO_PAPE_STRATEGY_HPP

#include <climits>
#include <deque>
#include <vector>

#include "ishortest_path_strategy.hpp"

using namespace std;

/**
 * @brief D'Esopo-Pape shortest-path strategy.
 *
 * Computes shortest paths in the residual network
 * using a deque-based relaxation mechanism that
 * often performs efficiently on sparse graphs.
 *
 * This strategy is used during Minimum-Cost
 * Maximum-Flow optimization.
 */
class DEsopoPapeStrategy
    : public IShortestPathStrategy
{
public:

    /**
     * @brief Finds a minimum-cost augmenting path.
     *
     * Executes the D'Esopo-Pape shortest-path
     * algorithm on the residual network and
     * reconstructs the resulting path.
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
            vertexCount,
            INVALID_EDGE
        );

        vector<bool> inQueue(
            vertexCount,
            false
        );

        deque<int> vertexDeque;

        distance[source] = 0;

        vertexDeque.push_back(
            source
        );

        inQueue[source] = true;

        while (!vertexDeque.empty()) {
            const int currentVertex =
                vertexDeque.front();

            vertexDeque.pop_front();

            inQueue[
                currentVertex
            ] = false;

            for (
                size_t edgeIndex = 0;
                edgeIndex < graph[currentVertex].size();
                ++edgeIndex
            ) {
                Edge& edge =
                    graph[currentVertex]
                         [edgeIndex];

                if (
                    edge.capacity > 0
                    && distance[currentVertex] != DISTANCE_INFINITY
                    && distance[currentVertex] + edge.cost < distance[edge.destination]
                ) {
                    const int previousDistance =
                        distance[edge.destination];

                    distance[edge.destination] =
                        distance[currentVertex]
                        + edge.cost;

                    parentVertex[
                        edge.destination
                    ] = currentVertex;

                    parentEdge[
                        edge.destination
                    ] = edgeIndex;

                    if (!inQueue[edge.destination]) {
                        if (previousDistance == DISTANCE_INFINITY) {
                            vertexDeque.push_back(
                                edge.destination
                            );
                        }
                        else {
                            vertexDeque.push_front(
                                edge.destination
                            );
                        }

                        inQueue[
                            edge.destination
                        ] = true;
                    }
                }
            }
        }

        return distance[sink] != DISTANCE_INFINITY;
    }
};

#endif // DESOPO_PAPE_STRATEGY_HPP