/**
 * @file flow_optimizer.cpp
 * @brief Minimum-Cost Maximum-Flow application.
 *
 * Builds a flow network from the input dataset,
 * executes the selected optimization algorithms,
 * and exports miner assignment results as JSON.
 */

#include <fstream>
#include <iostream>

#include "flow_optimizer.hpp"
#include "imaxflow_path_factory.hpp"
#include "ishortest_path_factory.hpp"

#include "foundation/core_utils_json.hpp"
#include "foundation/core_utils_stopwatch.hpp"

using namespace std;
using json = nlohmann::json;

/**
 * @brief Application entry point.
 *
 * Loads the input dataset, constructs a resource
 * allocation flow network, executes the selected
 * maximum-flow and shortest-path algorithms, and
 * exports optimization results as a JSON response.
 *
 * @param argc
 * Number of command-line arguments.
 *
 * @param argv
 * Command-line arguments.
 *
 * @return int
 * EXIT_SUCCESS on success, otherwise EXIT_FAILURE.
 */
int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Expected input file: <input.json>" << endl;
        return EXIT_FAILURE;
    }

    try {
        const json inputData = readInput(argv[1]);

        const auto [
            maxflowAlgorithm,
            mincostAlgorithm
        ] = extractAlgorithms(inputData);

        auto maxflowStrategy =
            createMaxFlowStrategy(
                maxflowAlgorithm
            );

        auto mincostStrategy =
            createShortestPathStrategy(
                mincostAlgorithm
            );

        const size_t minersCount =
            inputData["miners"].size();

        const size_t minesCount =
            inputData["mines"].size();

        constexpr size_t source = 0;

        const size_t sink =
            minersCount + minesCount + 1;

        const size_t verticesCount =
            sink + 1;

        FlowOptimizer solver(
            verticesCount,
            maxflowStrategy.get(),
            mincostStrategy.get()
        );

        for (size_t i = 0; i < minersCount; ++i) {
            solver.addEdge(
                source,
                i + 1,
                1,
                0
            );
        }

        for (size_t i = 0; i < minersCount; ++i) {

            const auto& miner =
                inputData["miners"][i];

            for (size_t j = 0; j < minesCount; ++j) {

                const auto& mine =
                    inputData["mines"][j];

                if (miner["resource"] != mine["resource"]) {
                    continue;
                }

                const size_t mineNode =
                    minersCount + j + 1;

                const int cost =
                    abs(
                        static_cast<int>(miner["x"]) -
                        static_cast<int>(mine["x"])
                    )
                    +
                    abs(
                        static_cast<int>(miner["y"]) -
                        static_cast<int>(mine["y"])
                    );

                solver.addEdge(
                    i + 1,
                    mineNode,
                    1,
                    cost
                );
            }
        }

        for (size_t j = 0; j < minesCount; ++j) {

            const auto& mine =
                inputData["mines"][j];

            solver.addEdge(
                minersCount + j + 1,
                sink,
                static_cast<int>(
                    mine["capacity"]
                ),
                0
            );
        }

        Stopwatch stopwatch;

        const auto result =
            solver.solve(
                source,
                sink
            );

        const double executionTimeMs =
            stopwatch.elapsedMilliseconds();

        const json assignments =
            buildAssignments(
                inputData,
                solver.getGraph(),
                minersCount,
                minesCount
            );

        const json output =
            buildFlowOutput(
                result,
                assignments,
                maxflowAlgorithm,
                mincostAlgorithm,
                executionTimeMs
            );

        cout << output.dump(4) << endl;
    }
    catch (const exception& exception) {
        cerr << exception.what() << endl;
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}