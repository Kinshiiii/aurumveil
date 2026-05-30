#ifndef ISHORTEST_PATH_FACTORY_HPP
#define ISHORTEST_PATH_FACTORY_HPP

#include <string>
#include <memory>

#include "bellman_ford_strategy.hpp"
#include "desopopape_strategy.hpp"

using namespace std;

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