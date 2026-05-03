#include <iostream>
#include <fstream>

#include "../include/nlohmann/json.hpp"

using namespace std;
using json = nlohmann::json;

int main(int argc, char* argv[]) {
    if (argc < 2) {
        return 1;
    }

    ifstream f(argv[1]);
    json data;
    f >> data;

    // implementation

    json result;
    result["example"] = "example";

    cout << result.dump();
}