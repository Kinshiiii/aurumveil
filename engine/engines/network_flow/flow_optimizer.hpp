#ifndef FLOW_OPTIMIZER_HPP
#define FLOW_OPTIMIZER_HPP

#include <vector>

#include "imaxflow_path_strategy.hpp"
#include "ishortest_path_strategy.hpp"

#include "foundation/core_utils_stopwatch.hpp"

using namespace std;

struct FlowStatistics {
    int maximumFlow{0};
    int minimumCost{0};

    int augmentationCount{0};

    double averagePathLength{0.0};
    int totalPathLength{0};

    double pathfindingTimeMs{0.0};
    double augmentationTimeMs{0.0};
    double totalTimeMs{0.0};
};

class FlowOptimizer {
public:
    FlowOptimizer(
        size_t vertices,
        IMaxFlowStrategy* maxflowStrategy,
        IShortestPathStrategy* mincostStrategy
    )
        : flowNetwork(vertices),
          maxflowStrategy(maxflowStrategy),
          mincostStrategy(mincostStrategy) {}

    void addEdge(
        size_t from,
        size_t to,
        int capacity,
        int cost
    ) {
        Edge forwardEdge{
            to,
            flowNetwork[to].size(),
            capacity,
            cost
        };

        Edge backwardEdge{
            from,
            flowNetwork[from].size(),
            0,
            -cost
        };

        flowNetwork[from].push_back(
            forwardEdge
        );

        flowNetwork[to].push_back(
            backwardEdge
        );
    }

    FlowStatistics solve(
        int source,
        int sink
    ) {
        Stopwatch totalStopwatch;
        Stopwatch phaseStopwatch;

        FlowStatistics statistics;

        vector<int> parentVertex;
        vector<size_t> parentEdge;
        vector<int> distance;

        while (true) {
            phaseStopwatch.restart();

            const bool pathFound =
                mincostStrategy->findPath(
                    flowNetwork,
                    source,
                    sink,
                    parentVertex,
                    parentEdge,
                    distance
                );

            statistics.pathfindingTimeMs +=
                phaseStopwatch
                    .elapsedMilliseconds();

            if (!pathFound) {
                break;
            }

            phaseStopwatch.restart();

            const int flow =
                maxflowStrategy->computeFlow(
                    flowNetwork,
                    source,
                    sink,
                    parentVertex,
                    parentEdge
                );

            ++statistics.augmentationCount;

            statistics.totalPathLength +=
                maxflowStrategy->calculatePathLength(
                    source,
                    sink,
                    parentVertex
                );

            if (flow <= 0) {
                break;
            }

            maxflowStrategy->augment(
                flowNetwork,
                source,
                sink,
                parentVertex,
                parentEdge,
                flow,
                statistics.minimumCost
            );

            statistics.maximumFlow +=
                flow;

            statistics.augmentationTimeMs +=
                phaseStopwatch
                    .elapsedMilliseconds();
        }

        statistics.totalTimeMs =
            totalStopwatch
                .elapsedMilliseconds();

        if (statistics.augmentationCount > 0) {
            statistics.averagePathLength =
                static_cast<double>(
                    statistics.totalPathLength
                ) / statistics.augmentationCount;
        }

        return statistics;
    }

    const FlowNetwork& getGraph() const {
        return flowNetwork;
    }

private:
    FlowNetwork flowNetwork;

    IMaxFlowStrategy* maxflowStrategy;
    IShortestPathStrategy* mincostStrategy;
};

#endif // FLOW_OPTIMIZER_HPP