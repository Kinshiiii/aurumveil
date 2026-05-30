#ifndef FLOW_NETWORK_HPP
#define FLOW_NETWORK_HPP

#include <vector>
#include <limits>

using namespace std;

constexpr int DISTANCE_INFINITY = numeric_limits<int>::max();
constexpr size_t INVALID_EDGE = numeric_limits<size_t>::max();

struct Edge {
    size_t destination;
    size_t reverseEdgeIndex;

    int capacity;
    int cost;
};

using FlowNetwork = vector<vector<Edge>>;

#endif //FLOW_NETWORK_HPP
