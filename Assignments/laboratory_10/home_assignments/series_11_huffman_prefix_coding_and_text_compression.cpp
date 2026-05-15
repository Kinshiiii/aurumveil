#include <algorithm>
#include <iostream>
#include <iomanip>
#include <map>
#include <queue>
#include <vector>

using namespace std;

struct HuffmanNode {
    char character{};
    size_t character_frequency{0};

    HuffmanNode* left_child{nullptr};
    HuffmanNode* right_child{nullptr};
};

struct CompareHuffmanNodes {
    bool operator()(const HuffmanNode* left_node, const HuffmanNode* right_node) const {
        return left_node->character_frequency > right_node->character_frequency;
    }
};

bool sort_by_character_frequency(const pair<char, size_t>& left_element, const pair<char, size_t>& right_element) {
    return left_element.second > right_element.second;
}

map<char, size_t> build_character_frequency_statistics(const string& input_text) {
    map<char, size_t> character_frequency_statistics;

    for (char current_character : input_text) {
        ++character_frequency_statistics[current_character];
    }

    return character_frequency_statistics;
}

vector<pair<char, size_t>> sort_character_statistics(const map<char, size_t>& character_frequency_statistics) {
    vector<pair<char, size_t>> sorted_character_statistics(
        character_frequency_statistics.begin(),
        character_frequency_statistics.end()
    );

    sort(
         sorted_character_statistics.begin(),
         sorted_character_statistics.end(),
         sort_by_character_frequency
    );

    return sorted_character_statistics;
}

priority_queue<HuffmanNode*, vector<HuffmanNode*>, CompareHuffmanNodes> build_huffman_priority_queue(const map<char, size_t>& character_frequency_statistics) {
    priority_queue<HuffmanNode*, vector<HuffmanNode*>, CompareHuffmanNodes> pq;

    for (const auto& pair : character_frequency_statistics) {
        auto* node = new HuffmanNode();
        node->character = pair.first;
        node->character_frequency = pair.second;
        pq.push(node);
    }

    return pq;
}

HuffmanNode* build_huffman_tree(priority_queue<HuffmanNode*, vector<HuffmanNode*>, CompareHuffmanNodes>& huffman_priority_queue) {
    if (huffman_priority_queue.empty()) {
        return nullptr;
    }

    while (huffman_priority_queue.size() > 1) {
        HuffmanNode* left_node = huffman_priority_queue.top();
        huffman_priority_queue.pop();

        HuffmanNode* right_node = huffman_priority_queue.top();
        huffman_priority_queue.pop();

        auto* parent_node = new HuffmanNode();

        parent_node->character = '\0';
        parent_node->character_frequency = left_node->character_frequency + right_node->character_frequency;
        parent_node->left_child = left_node;
        parent_node->right_child = right_node;

        huffman_priority_queue.push(parent_node);
    }

    return huffman_priority_queue.top();
}

void generate_huffman_codes(const HuffmanNode* current_node, const string& current_code, map<char, string>& huffman_codes) {
    if (!current_node) {
        return;
    }

    if (!current_node->left_child && !current_node->right_child) {
        huffman_codes[current_node->character] = current_code.empty() ? "0" : current_code;
        return;
    }

    generate_huffman_codes(current_node->left_child, current_code + "0", huffman_codes);
    generate_huffman_codes(current_node->right_child, current_code + "1", huffman_codes);
}

string compress_text(const string& input_text, const map<char, string>& huffman_codes) {
    string compressed_text;

    for (char current_character : input_text) {
        compressed_text += huffman_codes.at(current_character);
    }

    return compressed_text;
}

size_t compute_original_text_size(const string& input_text) {
    return input_text.length() * 8;
}

size_t compute_compressed_text_size(const string& compressed_text) {
    return compressed_text.size();
}

double compute_compression_percentage(size_t original_text_size, size_t compressed_text_size) {
    if (original_text_size == 0) {
        return 0.0;
    }

    return (1.0 - static_cast<double>(compressed_text_size) / static_cast<double>(original_text_size)) * 100.0;
}

void display_character_statistics(const vector<pair<char, size_t>>& sorted_character_statistics) {
    cout << endl;
    cout << "Character frequency:" << endl;

    for (const auto& entry : sorted_character_statistics) {
        cout << "  - '" << entry.first << "': "
             << entry.second << endl;
    }
}

void display_huffman_codes(const map<char, string>& huffman_codes) {
    cout << endl;
    cout << "Huffman codes:" << endl;

    for (const auto& entry : huffman_codes) {
        cout << "  - '" << entry.first << "': "
             << entry.second << endl;
    }
}

void clean_up_tree(HuffmanNode* node) {
    if (!node) {
        return;
    }

    clean_up_tree(node->left_child);
    clean_up_tree(node->right_child);

    delete node;
}

void execute_huffman_compression_workflow(const string& input_text) {
    auto character_stats = build_character_frequency_statistics(input_text);
    auto sorted_stats = sort_character_statistics(character_stats);

    cout << endl;
    cout << "Huffman compression workflow started..." << endl;

    display_character_statistics(sorted_stats);

    auto pq = build_huffman_priority_queue(character_stats);
    HuffmanNode* root = build_huffman_tree(pq);

    map<char, string> huffman_codes;
    generate_huffman_codes(root, "", huffman_codes);

    display_huffman_codes(huffman_codes);

    string compressed = compress_text(input_text, huffman_codes);

    size_t orig_size = compute_original_text_size(input_text);
    size_t comp_size = compute_compressed_text_size(compressed);

    cout << endl << endl;
    cout << "Compression summary (Huffman coding algorithm):" << endl;

    cout << "  - Original text size: "
         << orig_size
         << " bits" << endl;

    cout << "  - Compressed text size: "
         << comp_size
         << " bits" << endl;

    cout << "  - Compression ratio: "
         << fixed << setprecision(2)
         << compute_compression_percentage(orig_size, comp_size)
         << "%" << endl;

    cout << endl;
    cout << "Huffman encoding completed successfully." << endl;

    clean_up_tree(root);
}

void initialize_huffman_compression_workflow() {
    string input_text;

    cout << "Enter the English text:" << endl;
    getline(cin, input_text);

    if (input_text.empty()) {
        cout << endl;

        cout << "Huffman Compression:" << endl
             << "  - The input text is EMPTY" << endl
             << "  - Compression cannot be performed on an empty text" << endl
             << endl;

        return;
    }

    execute_huffman_compression_workflow(
        input_text
    );
}

int main() {
    initialize_huffman_compression_workflow();
    return 0;
}
