#ifndef DESOPO_PAPE_STRATEGY_HPP
#define DESOPO_PAPE_STRATEGY_HPP

#include <climits>
#include <deque>
#include <vector>

#include "shortest_path_strategy.hpp"

using namespace std;

class DEsopoPapeStrategy
    : public IShortestPathStrategy
{
public:

    bool findPath(
        Graph& graph,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<int>& parentEdge,
        vector<int>& distance
    ) override {
        constexpr int INF = INT_MAX;

        int vertexCount =
            static_cast<int>(
                graph.size()
            );

        distance.assign(
            vertexCount,
            INF
        );

        parentVertex.assign(
            vertexCount,
            -1
        );

        parentEdge.assign(
            vertexCount,
            -1
        );

        vector<bool> inQueue(
            vertexCount,
            false
        );

        deque<int> vertexDeque;

        distance[source] = 0;

        vertexDeque.push_back(source);

        inQueue[source] = true;

        while (!vertexDeque.empty()) {
            int currentVertex =
                vertexDeque.front();

            vertexDeque.pop_front();

            inQueue[currentVertex] = false;

            for (
                size_t edgeIndex = 0;
                edgeIndex < graph[currentVertex].size();
                ++edgeIndex
            ) {
                Edge& edge =
                    graph[currentVertex]
                         [edgeIndex];

                if (
                    edge.capacity > 0 &&
                    distance[currentVertex] != INF &&
                    distance[currentVertex] + edge.cost <
                    distance[edge.to]
                ) {
                    int previousDistance =
                        distance[edge.to];

                    distance[edge.to] =
                        distance[currentVertex] +
                        edge.cost;

                    parentVertex[edge.to] =
                        currentVertex;

                    parentEdge[edge.to] =
                        static_cast<int>(
                            edgeIndex
                        );

                    if (!inQueue[edge.to]) {

                        if (
                            previousDistance == INF
                        ) {
                            vertexDeque.push_back(
                                edge.to
                            );

                        } else {

                            vertexDeque.push_front(
                                edge.to
                            );
                        }

                        inQueue[edge.to] = true;
                    }
                }
            }
        }

        return distance[sink] != INF;
    }
};

#endif // DESOPO_PAPE_STRATEGY_HPP
