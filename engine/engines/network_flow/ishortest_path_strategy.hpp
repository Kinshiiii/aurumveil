#ifndef ISHORTEST_PATH_STRATEGY_HPP
#define ISHORTEST_PATH_STRATEGY_HPP

#include <vector>

#include "flow_network.hpp"

using namespace std;

class IShortestPathStrategy {
public:

    virtual bool findPath(
        FlowNetwork& flowNetwork,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<size_t>& parentEdge,
        vector<int>& distance
    ) = 0;

    virtual ~IShortestPathStrategy() = default;
};

#endif // ISHORTEST_PATH_STRATEGY_HPP