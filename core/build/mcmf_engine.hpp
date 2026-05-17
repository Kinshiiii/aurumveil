#pragma once

#include <vector>

#include "shortest_path_strategy.hpp"
#include "imaxflow_strategy.hpp"

using namespace std;

struct MCMFResult {
    int flow;
    int cost;
};

class MinCostMaxFlow {
private:
    Graph graph;

    IMaxFlowStrategy* maxflowStrategy;
    IShortestPathStrategy* mincostStrategy;

public:
    MinCostMaxFlow(
        int vertices,
        IMaxFlowStrategy* maxflow,
        IShortestPathStrategy* mincost
    )
        : graph(vertices),
          maxflowStrategy(maxflow),
          mincostStrategy(mincost) {}

    void addEdge(
        int from,
        int to,
        int capacity,
        int cost
    ) {

        Edge forward{
            to,
            (int)graph[to].size(),
            capacity,
            cost
        };

        Edge backward{
            from,
            (int)graph[from].size(),
            0,
            -cost
        };

        graph[from].push_back(forward);
        graph[to].push_back(backward);
    }

    MCMFResult solve(
        int source,
        int sink
    ) {

        int totalFlow = 0;
        int totalCost = 0;

        vector<int> parentVertex;
        vector<int> parentEdge;
        vector<int> distance;

        while (
            mincostStrategy->findPath(
                graph,
                source,
                sink,
                parentVertex,
                parentEdge,
                distance
            )
        ) {

            int flow = maxflowStrategy->computeFlow(
                graph,
                source,
                sink,
                parentVertex,
                parentEdge
            );

            maxflowStrategy->augment(
                graph,
                source,
                sink,
                parentVertex,
                parentEdge,
                flow,
                totalCost
            );

            totalFlow += flow;
        }

        return {
            totalFlow,
            totalCost
        };
    }
};