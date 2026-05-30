/**
 * @file imaxflow_path_factory.hpp
 * @brief Maximum-flow strategy factory.
 *
 * Provides creation utilities for maximum-flow
 * algorithm implementations used by the flow
 * optimization engine.
 */

#ifndef IMAXFLOW_PATH_FACTORY_HPP
#define IMAXFLOW_PATH_FACTORY_HPP

#include <string>
#include <memory>

#include "imaxflow_path_strategy.hpp"

#include "ford_fulkerson_strategy.hpp"
#include "edmonds_karp_strategy.hpp"

using namespace std;

/**
 * @brief Creates a maximum-flow strategy.
 *
 * Instantiates the selected maximum-flow algorithm
 * implementation based on its textual identifier.
 *
 * Supported algorithms:
 * - Ford-Fulkerson
 * - Edmonds-Karp
 *
 * @param strategyName
 * Maximum-flow algorithm name.
 *
 * @return unique_ptr<IMaxFlowStrategy>
 * Strategy instance implementing the requested
 * algorithm.
 *
 * @throws runtime_error
 * Raised when the requested algorithm is not
 * supported.
 */
inline unique_ptr<IMaxFlowStrategy> createMaxFlowStrategy(const string& strategyName) {
    if (strategyName == "Ford-Fulkerson") {
        return make_unique<FordFulkersonStrategy>();
    }

    if (strategyName == "Edmonds-Karp") {
        return make_unique<EdmondsKarpStrategy>();
    }

    throw runtime_error(
        "Unsupported maximum flow algorithm: "
        + strategyName
    );
}

#endif // IMAXFLOW_PATH_FACTORY_HPP