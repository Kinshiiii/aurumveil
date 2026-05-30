#ifndef BELLMAN_FORD_STRATEGY_HPP
#define BELLMAN_FORD_STRATEGY_HPP

#include <queue>
#include <vector>

#include "ishortest_path_strategy.hpp"

using namespace std;

class BellmanFordStrategy
    : public IShortestPathStrategy
{
public:

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