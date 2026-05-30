#ifndef EDMONDS_KARP_STRATEGY_HPP
#define EDMONDS_KARP_STRATEGY_HPP

#include <algorithm>

#include "imaxflow_path_strategy.hpp"

using namespace std;

class EdmondsKarpStrategy
    : public IMaxFlowStrategy
{
public:
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