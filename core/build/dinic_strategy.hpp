#ifndef DINIC_STRATEGY_HPP
#define DINIC_STRATEGY_HPP

#include <algorithm>
#include <queue>
#include <vector>

#include "imaxflow_strategy.hpp"

using namespace std;

class DinicStrategy
    : public IMaxFlowStrategy
{
private:

    bool buildLevelGraph(
        Graph& graph,
        int source,
        int sink,
        vector<int>& level
    ) {
        level.assign(
            graph.size(),
            -1
        );

        queue<int> vertexQueue;

        level[source] = 0;

        vertexQueue.push(source);

        while (!vertexQueue.empty()) {
            int currentVertex =
                vertexQueue.front();

            vertexQueue.pop();

            for (const Edge& edge : graph[currentVertex]) {
                if (
                    edge.capacity > 0 &&
                    level[edge.to] < 0
                ) {
                    level[edge.to] =
                        level[currentVertex] + 1;

                    vertexQueue.push(edge.to);
                }
            }
        }

        return level[sink] >= 0;
    }

    int sendBlockingFlow(
        Graph& graph,
        int currentVertex,
        int sink,
        int flowToPush,
        vector<int>& level,
        vector<size_t>& edgeIndex,
        vector<int>& parentVertex,
        vector<int>& parentEdge
    ) {
        if (currentVertex == sink) {
            return flowToPush;
        }

        for (
            size_t& edgePtr = edgeIndex[currentVertex];
            edgePtr < graph[currentVertex].size();
            ++edgePtr
        ) {
            Edge& edge =
                graph[currentVertex]
                     [edgePtr];

            if (
                edge.capacity > 0 &&
                level[edge.to] ==
                    level[currentVertex] + 1
            ) {
                parentVertex[edge.to] =
                    currentVertex;

                parentEdge[edge.to] =
                    static_cast<int>(
                        edgePtr
                    );

                int pushedFlow =
                    sendBlockingFlow(
                        graph,
                        edge.to,
                        sink,
                        min(
                            flowToPush,
                            edge.capacity
                        ),
                        level,
                        edgeIndex,
                        parentVertex,
                        parentEdge
                    );

                if (pushedFlow > 0) {
                    return pushedFlow;
                }
            }
        }

        return 0;
    }

public:

    int computeFlow(
        Graph& graph,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<int>& parentEdge
    ) override {
        constexpr int INF = 1e9;

        vector<int> level;

        if (
            !buildLevelGraph(
                graph,
                source,
                sink,
                level
            )
        ) {
            return 0;
        }

        parentVertex.assign(
            graph.size(),
            -1
        );

        parentEdge.assign(
            graph.size(),
            -1
        );

        vector<size_t> edgeIndex(
            graph.size(),
            0
        );

        return sendBlockingFlow(
            graph,
            source,
            sink,
            INF,
            level,
            edgeIndex,
            parentVertex,
            parentEdge
        );
    }

    void augment(
        Graph& graph,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<int>& parentEdge,
        int flow,
        int& totalCost
    ) override {
        for (
            int v = sink;
            v != source;
            v = parentVertex[v]
        ) {
            int u =
                parentVertex[v];

            Edge& edge =
                graph[u]
                     [parentEdge[v]];

            Edge& reverse =
                graph[v]
                     [edge.rev];

            edge.capacity -= flow;
            reverse.capacity += flow;

            totalCost +=
                flow * edge.cost;
        }
    }
};

#endif // DINIC_STRATEGY_HPP