#ifndef BELLMAN_FORD_STRATEGY_HPP
#define BELLMAN_FORD_STRATEGY_HPP

#include <deque>
#include <vector>
#include <queue>
#include <limits>

static constexpr int INF = numeric_limits<int>::max();

#include "shortest_path_strategy.hpp"

using namespace std;

class BellmanFordStrategy
    : public IShortestPathStrategy {

public:

    bool findPath(
        Graph& graph,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<int>& parentEdge,
        vector<int>& distance
    ) override {

        int numVertices =
            static_cast<int>(graph.size());

        distance.assign(
            numVertices,
            INF
        );

        parentVertex.assign(
            numVertices,
            -1
        );

        parentEdge.assign(
            numVertices,
            -1
        );

        vector<bool> inQueue(
            numVertices,
            false
        );

        

        vector<int> relaxCount(
            numVertices,
            0
        );

        queue<int> queue;

        distance[source] = 0;

        queue.push(source);

        inQueue[source] = true;

        while (!queue.empty()) {

            int u = queue.front();

            queue.pop();

            inQueue[u] = false;

            

            for (
                size_t edgeIndex = 0;
                edgeIndex < graph[u].size();
                ++edgeIndex
            ) {

                Edge& edge =
                    graph[u][edgeIndex];

                int v = edge.to;

                if (edge.capacity <= 0) {
                    continue;
                }

                if (distance[u] == INF) {
                    continue;
                }

                if (
                    distance[v] >
                    distance[u] + edge.cost
                ) {

                    distance[v] =
                        distance[u] + edge.cost;

                    parentVertex[v] = u;

                    parentEdge[v] =
                        static_cast<int>(edgeIndex);

                    relaxCount[v]++;

                    if (
                        relaxCount[v] > numVertices
                    ) {
                        return false;
                    }

                    if (!inQueue[v]) {

                        queue.push(v);

                        inQueue[v] = true;
                    }
                }
            }
        }

        return distance[sink] != INF;
    }
};

#endif // BELLMAN_FORD_STRATEGY_HPP