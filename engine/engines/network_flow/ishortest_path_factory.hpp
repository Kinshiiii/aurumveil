/**
 * @file ishortest_path_factory.hpp
 * @brief Shortest-path strategy factory.
 *
 * Provides creation utilities for shortest-path
 * algorithm implementations used by the flow
 * optimization engine.
 */

#ifndef ISHORTEST_PATH_FACTORY_HPP
#define ISHORTEST_PATH_FACTORY_HPP

#include <string>
#include <memory>

#include "bellman_ford_strategy.hpp"
#include "desopopape_strategy.hpp"

using namespace std;

/**
 * @brief Creates a shortest-path strategy.
 *
 * Instantiates the selected shortest-path
 * algorithm implementation based on its textual
 * identifier.
 *
 * Supported algorithms:
 * - Bellman-Ford
 * - D'Esopo-Pape
 *
 * @param strategyName
 * Shortest-path algorithm name.
 *
 * @return unique_ptr<IShortestPathStrategy>
 * Strategy instance implementing the requested
 * algorithm.
 *
 * @throws runtime_error
 * Raised when the requested algorithm is not
 * supported.
 */
inline unique_ptr<IShortestPathStrategy> createShortestPathStrategy(const string& strategyName) {
    if (strategyName == "Bellman-Ford") {
        return make_unique<BellmanFordStrategy>();
    }

    if (strategyName == "D'Esopo-Pape") {
        return make_unique<DEsopoPapeStrategy>();
    }

    throw runtime_error(
        "Unsupported shortest path algorithm: "
        + strategyName
    );
}

#endif // ISHORTEST_PATH_FACTORY_HPP