#ifndef EDMONDS_KARP_STRATEGY_HPP
#define EDMONDS_KARP_STRATEGY_HPP

#include <algorithm>

#include "imaxflow_strategy.hpp"

using namespace std;

class EdmondsKarpStrategy
    : public IMaxFlowStrategy
{
public:

    int computeFlow(
        Graph& graph,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<int>& parentEdge
    ) override {
        constexpr int INF = 1e9;

        int pathFlow = INF;
        int currentVertex = sink;

        while (currentVertex != source) {
            int previousVertex = parentVertex[currentVertex];

            Edge& edge = graph[previousVertex][parentEdge[currentVertex]];

            pathFlow = min(
                pathFlow,
                edge.capacity
            );

            currentVertex = previousVertex;
        }

        return pathFlow;
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
        int currentVertex = sink;

        while (currentVertex != source) {
            int previousVertex = parentVertex[currentVertex];

            Edge& edge = graph[previousVertex][parentEdge[currentVertex]];
            Edge& reverse = graph[currentVertex][edge.rev];

            edge.capacity -= flow;
            reverse.capacity += flow;

            totalCost += flow * edge.cost;

            currentVertex = previousVertex;
        }
    }
};

#endif // EDMONDS_KARP_STRATEGY_HPP