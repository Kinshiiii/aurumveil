#ifndef FORD_FULKERSON_STRATEGY_HPP
#define FORD_FULKERSON_STRATEGY_HPP

#include <algorithm>

#include "imaxflow_strategy.hpp"

using namespace std;

class FordFulkersonStrategy
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

        for (int v = sink; v != source; v = parentVertex[v]) {
            int u = parentVertex[v];

            Edge& edge = graph[u][parentEdge[v]];

            pathFlow = min(
                pathFlow,
                edge.capacity
            );
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
        for (int v = sink; v != source; v = parentVertex[v]) {
            int previousVertex = parentVertex[v];

            Edge& edge = graph[previousVertex][parentEdge[v]];

            Edge& reverse = graph[v][edge.rev];

            edge.capacity -= flow;
            reverse.capacity += flow;

            totalCost += flow * edge.cost;
        }
    }
};

#endif // FORD_FULKERSON_STRATEGY_HPP