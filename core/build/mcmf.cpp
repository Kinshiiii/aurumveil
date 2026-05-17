#include <fstream>
#include <iostream>
#include <iterator>

#include "../include/nlohmann/json.hpp"

#include "mcmf_engine.hpp"
#include "strategy_factory.hpp"
#include "maxflow_factory.hpp"

using namespace std;
using json = nlohmann::json;

int main(int argc, char* argv[]) {

    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string input;

    if (argc > 1) {

        ifstream file(argv[1]);

        if (!file) {
            return 1;
        }

        input.assign(
            istreambuf_iterator<char>(file),
            {}
        );
    }
    else {
        input.assign(
            istreambuf_iterator<char>(cin),
            {}
        );
    }

    json j = json::parse(input);

    string maxflowName = j["config"]["maxflow"];
    string mincostName = j["config"]["mincost"];

    auto maxflow = createMaxFlowStrategy(maxflowName);
    auto mincost = createStrategy(mincostName);

    int minersCount = j["miners"].size();
    int minesCount = j["mines"].size();

    int source = 0;
    int sink = minersCount + minesCount + 1;

    int totalVertices = sink + 1;

    MinCostMaxFlow solver(
        totalVertices,
        maxflow.get(),
        mincost.get()
    );

    for (int i = 0; i < minersCount; ++i) {
        solver.addEdge(source, i + 1, 1, 0);
    }

    for (int i = 0; i < minersCount; ++i) {

        auto& miner = j["miners"][i];

        for (int k = 0; k < minesCount; ++k) {

            auto& mine = j["mines"][k];

            int mineNode = minersCount + k + 1;

            int cost = abs(
                (int)miner["x"] - (int)mine["x"]
            ) + abs(
                (int)miner["y"] - (int)mine["y"]
            );

            solver.addEdge(
                i + 1,
                mineNode,
                1,
                cost
            );
        }
    }

    for (int k = 0; k < minesCount; ++k) {

        auto& mine = j["mines"][k];

        int mineNode = minersCount + k + 1;

        solver.addEdge(
            mineNode,
            sink,
            (int)mine["capacity"],
            0
        );
    }

    auto result = solver.solve(source, sink);

    json output;

    output["maxflow"] = maxflowName;
    output["mincost"] = mincostName;
    output["max_flow"] = result.flow;
    output["min_cost"] = result.cost;

    cout << output.dump(4) << endl;

    return 0;
}
