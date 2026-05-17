#ifndef IMAXFLOW_STRATEGY_HPP
#define IMAXFLOW_STRATEGY_HPP

#include <vector>

using namespace std;

struct Edge;

using Graph = vector<vector<Edge>>;

class IMaxFlowStrategy
{
public:

    virtual int computeFlow(
        Graph& graph,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<int>& parentEdge
    ) = 0;

    virtual void augment(
        Graph& graph,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<int>& parentEdge,
        int flow,
        int& totalCost
    ) = 0;

    virtual ~IMaxFlowStrategy() = default;
};

#endif // IMAXFLOW_STRATEGY_HPP