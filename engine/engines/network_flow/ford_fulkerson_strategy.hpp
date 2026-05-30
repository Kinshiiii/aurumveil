#ifndef FORD_FULKERSON_STRATEGY_HPP
#define FORD_FULKERSON_STRATEGY_HPP

#include <algorithm>

#include "imaxflow_path_strategy.hpp"

using namespace std;

class FordFulkersonStrategy
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