#ifndef IMAXFLOW_PATH_STRATEGY_HPP
#define IMAXFLOW_PATH_STRATEGY_HPP

#include <vector>

#include "flow_network.hpp"

using namespace std;

class IMaxFlowStrategy {
public:

    virtual int computeFlow(
        FlowNetwork& flowNetwork,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<size_t>& parentEdge
    ) = 0;

    virtual void augment(
        FlowNetwork& flowNetwork,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<size_t>& parentEdge,
        int flow,
        int& totalCost
    ) = 0;

    virtual int calculatePathLength(
        int source,
        int sink,
        const vector<int>& parentVertex
    ) {
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

    virtual ~IMaxFlowStrategy() = default;
};

#endif // IMAXFLOW_PATH_STRATEGY_HPP