#include <iostream>
#include <fstream>
#include <string>
#include <iterator>

#include "../include/nlohmann/json.hpp"

using namespace std;
using json = nlohmann::json;

int main(int argc, char* argv[]) {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string input;

    if (argc > 1) {
        ifstream f(argv[1]);
        if (!f) return 1;
        input.assign(istreambuf_iterator<char>(f), {});
    } else {
        input.assign(istreambuf_iterator<char>(cin), {});
    }

    json j = json::parse(input);

    cout << j.dump(2) << endl;
}
