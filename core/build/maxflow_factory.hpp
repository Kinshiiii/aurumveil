#ifndef MAX_FLOW_STRATEGY_FACTORY_HPP
#define MAX_FLOW_STRATEGY_FACTORY_HPP

#include <memory>
#include <string>

#include "imaxflow_strategy.hpp"

#include "dinic_strategy.hpp"
#include "edmonds_karp_strategy.hpp"
#include "ford_fulkerson_strategy.hpp"

using namespace std;

inline unique_ptr<IMaxFlowStrategy> createMaxFlowStrategy(
    const string& strategyName
) {
    if (strategyName == "Ford-Fulkerson") {
        return make_unique<FordFulkersonStrategy>();
    }

    if (strategyName == "Edmonds-Karp") {
        return make_unique<EdmondsKarpStrategy>();
    }

    if (strategyName == "Dinic") {
        return make_unique<DinicStrategy>();
    }

    return make_unique<FordFulkersonStrategy>();
}

#endif // MAX_FLOW_STRATEGY_FACTORY_HPP