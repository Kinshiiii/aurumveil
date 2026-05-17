#ifndef STRATEGY_FACTORY_HPP
#define STRATEGY_FACTORY_HPP

#include <memory>
#include <stdexcept>
#include <string>

#include "bellman_ford_strategy.hpp"
#include "desopopape_strategy.hpp"

using namespace std;

inline unique_ptr<IShortestPathStrategy> createStrategy(const string& name) {
    if (name == "Bellman-Ford") {
        return make_unique<BellmanFordStrategy>();
    }

    if (name == "DESO") {
        return make_unique<DEsopoPapeStrategy>();
    }

    throw runtime_error("Unknown strategy: " + name);
}

#endif // STRATEGY_FACTORY_HPP