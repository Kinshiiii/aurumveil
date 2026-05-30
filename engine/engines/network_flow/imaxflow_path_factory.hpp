#ifndef IMAXFLOW_PATH_FACTORY_HPP
#define IMAXFLOW_PATH_FACTORY_HPP

#include <string>
#include <memory>

#include "imaxflow_path_strategy.hpp"

#include "ford_fulkerson_strategy.hpp"
#include "edmonds_karp_strategy.hpp"

using namespace std;

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