/**
 * @file flow_optimizer.hpp
 * @brief Minimum-Cost Maximum-Flow optimization engine.
 *
 * Provides the core optimization framework used
 * for resource allocation between miners and mines.
 *
 * The optimizer combines a shortest-path strategy
 * with a maximum-flow strategy to compute a
 * minimum-cost maximum-flow solution.
 */

#ifndef FLOW_OPTIMIZER_HPP
#define FLOW_OPTIMIZER_HPP

#include <vector>

#include "imaxflow_path_strategy.hpp"
#include "ishortest_path_strategy.hpp"

#include "foundation/core_utils_stopwatch.hpp"

using namespace std;

/**
 * @brief Flow optimization statistics.
 *
 * Stores optimization results, execution metrics,
 * and benchmarking information generated during
 * a Minimum-Cost Maximum-Flow computation.
 */
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

/**
 * @brief Minimum-Cost Maximum-Flow optimizer.
 *
 * Maintains a residual flow network and coordinates
 * shortest-path and maximum-flow strategies to
 * compute an optimal resource allocation.
 */
class FlowOptimizer {
public:

    /**
     * @brief Creates a flow optimizer.
     *
     * Initializes the flow network and attaches
     * the selected maximum-flow and shortest-path
     * strategies.
     *
     * @param vertices
     * Number of vertices in the flow network.
     *
     * @param maxflowStrategy
     * Maximum-flow strategy implementation.
     *
     * @param mincostStrategy
     * Shortest-path strategy implementation.
     */
    FlowOptimizer(
        size_t vertices,
        IMaxFlowStrategy* maxflowStrategy,
        IShortestPathStrategy* mincostStrategy
    )
        : flowNetwork(vertices),
          maxflowStrategy(maxflowStrategy),
          mincostStrategy(mincostStrategy) {}

    /**
     * @brief Adds a directed edge to the network.
     *
     * Creates both forward and residual edges and
     * inserts them into the residual graph.
     *
     * @param from
     * Source vertex.
     *
     * @param to
     * Destination vertex.
     *
     * @param capacity
     * Edge capacity.
     *
     * @param cost
     * Edge traversal cost.
     */
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

    /**
     * @brief Solves the Minimum-Cost Maximum-Flow problem.
     *
     * Repeatedly searches for augmenting paths,
     * computes admissible flow values, updates the
     * residual network, and gathers execution
     * statistics until no additional path exists.
     *
     * @param source
     * Source vertex.
     *
     * @param sink
     * Sink vertex.
     *
     * @return FlowStatistics
     * Optimization result and performance metrics.
     */
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

    /**
     * @brief Returns the residual flow network.
     *
     * Provides read-only access to the current
     * network state after optimization.
     *
     * @return const FlowNetwork&
     * Residual flow network.
     */
    const FlowNetwork& getGraph() const {
        return flowNetwork;
    }

private:

    /// Residual flow network.
    FlowNetwork flowNetwork;

    /// Maximum-flow strategy.
    IMaxFlowStrategy* maxflowStrategy;

    /// Shortest-path strategy.
    IShortestPathStrategy* mincostStrategy;
};

#endif // FLOW_OPTIMIZER_HPP