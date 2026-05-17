#pragma once

#include <vector>

using namespace std;

struct Edge {
    int to;
    int rev;
    int capacity;
    int cost;
};

using Graph = vector<vector<Edge>>;

class IShortestPathStrategy {
public:
    virtual bool findPath(
        Graph& graph,
        int source,
        int sink,
        vector<int>& parentVertex,
        vector<int>& parentEdge,
        vector<int>& distance
    ) = 0;

    virtual ~IShortestPathStrategy() = default;
};