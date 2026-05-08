#include <algorithm>
#include <fstream>
#include <iostream>
#include <limits>
#include <vector>

#include "../include/nlohmann/json.hpp"

using namespace std;
using json = nlohmann::json;

struct Dwarf {
    string id;
    int loudness;
};

vector<Dwarf> segment_tree;
vector<Dwarf> dwarfs;

const Dwarf neutral_element = {
    "",
    numeric_limits<int>::min()
};

Dwarf loudness_max(const Dwarf& a, const Dwarf& b) {
    if (a.loudness >= b.loudness) {
        return a;
    }

    return b;
}

void build_tree(size_t node_index, size_t node_left, size_t node_right) {
    if (node_left == node_right) {
        segment_tree[node_index] = dwarfs[node_left];
        return;
    }

    size_t mid = (node_left + node_right) / 2;

    build_tree(2 * node_index, node_left, mid);
    build_tree(2 * node_index + 1, mid + 1, node_right);

    segment_tree[node_index] = loudness_max(
        segment_tree[2 * node_index],
        segment_tree[2 * node_index + 1]
    );
}

Dwarf query_range(
    size_t node_index,
    size_t node_left,
    size_t node_right,
    size_t query_left,
    size_t query_right
) {
    if (node_right < query_left || query_right < node_left) {
        return neutral_element;
    }

    if (query_left <= node_left && node_right <= query_right) {
        return segment_tree[node_index];
    }

    size_t mid = (node_left + node_right) / 2;

    Dwarf left_result = query_range(
        2 * node_index,
        node_left,
        mid,
        query_left,
        query_right
    );

    Dwarf right_result = query_range(
        2 * node_index + 1,
        mid + 1,
        node_right,
        query_left,
        query_right
    );

    return loudness_max(left_result, right_result);
}

void load_data_from_json(const json& data) {
    dwarfs.push_back(neutral_element);

    if (data.contains("points")) {
        for (const auto& point : data["points"]) {
            dwarfs.push_back({
                point.value("id", ""),
                point.value("loudness", 0)
            });
        }
    }
}

void output_result(const Dwarf& result) {
    json output;

    output["id"] = result.id;
    output["loudness"] = result.loudness;

    cout << output.dump(4) << endl;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage: program <input_file.json>" << endl;
        return 1;
    }

    ifstream file(argv[1]);

    if (!file) {
        cerr << "Error: Cannot open file." << endl;
        return 1;
    }

    json input_json;
    file >> input_json;

    load_data_from_json(input_json);

    if (dwarfs.size() <= 1) {
        output_result(neutral_element);
        return 0;
    }

    size_t node_right = dwarfs.size() - 1;

    segment_tree.resize(4 * node_right + 1, neutral_element);

    build_tree(1, 1, node_right);

    size_t query_left = 1;
    size_t query_right = node_right;

    if (input_json.contains("range") && input_json["range"].size() == 2) {
        int left = input_json["range"][0];
        int right = input_json["range"][1];

        left = max(left, 1);
        right = min(right, static_cast<int>(node_right));

        if (left <= right) {
            query_left = static_cast<size_t>(left);
            query_right = static_cast<size_t>(right);
        }
    }

    Dwarf result = query_range(
        1,
        1,
        node_right,
        query_left,
        query_right
    );

    output_result(result);

    return 0;
}