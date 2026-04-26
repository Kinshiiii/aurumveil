#include <iostream>

using namespace std;

enum class Color {
    RED,
    BLACK
};

struct Node {
    int key{};
    Node* parent{nullptr};
    Node* left{nullptr};
    Node* right{nullptr};
    Color color{Color::RED};
};

struct RBTree {
    Node* root{nullptr};
    Node* nil{nullptr};
};

RBTree create_tree() {
    RBTree tree;

    Node* sentinel = new Node{};
    sentinel->color = Color::BLACK;
    sentinel->left = sentinel;
    sentinel->right = sentinel;
    sentinel->parent = sentinel;

    tree.nil = sentinel;
    tree.root = sentinel;

    return tree;
}

void delete_subtree(Node* node, Node* nil) {
    if (node == nil) {
        return;
    }

    delete_subtree(node->left, nil);
    delete_subtree(node->right, nil);
    delete node;
}

void destroy_tree(RBTree* tree) {
    delete_subtree(tree->root, tree->nil);
    delete tree->nil;
}

void rotate_left(RBTree* tree, Node* node) {
    Node* right_child = node->right;
    node->right = right_child->left;

    if (right_child->left != tree->nil) {
        right_child->left->parent = node;
    }

    right_child->parent = node->parent;

    if (node->parent == tree->nil) {
        tree->root = right_child;
    } else if (node == node->parent->left) {
        node->parent->left = right_child;
    } else {
        node->parent->right = right_child;
    }

    right_child->left = node;
    node->parent = right_child;
}

void rotate_right(RBTree* tree, Node* node) {
    Node* left_child = node->left;
    node->left = left_child->right;

    if (left_child->right != tree->nil) {
        left_child->right->parent = node;
    }

    left_child->parent = node->parent;

    if (node->parent == tree->nil) {
        tree->root = left_child;
    } else if (node == node->parent->right) {
        node->parent->right = left_child;
    } else {
        node->parent->left = left_child;
    }

    left_child->right = node;
    node->parent = left_child;
}

Node* create_node(RBTree* tree, int key) {
    Node* node = new Node{};
    node->key = key;
    node->left = tree->nil;
    node->right = tree->nil;
    node->parent = tree->nil;
    return node;
}

void insert_fixup(RBTree* tree, Node* node) {
    while (node->parent->color == Color::RED) {
        Node* uncle_node;

        if (node->parent == node->parent->parent->left) {
            uncle_node = node->parent->parent->right;

            if (uncle_node->color == Color::RED) {
                node->parent->color = Color::BLACK;
                uncle_node->color = Color::BLACK;
                node->parent->parent->color = Color::RED;
                node = node->parent->parent;
            } else {
                if (node == node->parent->right) {
                    node = node->parent;
                    rotate_left(tree, node);
                }

                node->parent->color = Color::BLACK;
                node->parent->parent->color = Color::RED;
                rotate_right(tree, node->parent->parent);
            }
        } else {
            uncle_node = node->parent->parent->left;

            if (uncle_node->color == Color::RED) {
                node->parent->color = Color::BLACK;
                uncle_node->color = Color::BLACK;
                node->parent->parent->color = Color::RED;
                node = node->parent->parent;
            } else {
                if (node == node->parent->left) {
                    node = node->parent;
                    rotate_right(tree, node);
                }

                node->parent->color = Color::BLACK;
                node->parent->parent->color = Color::RED;
                rotate_left(tree, node->parent->parent);
            }
        }
    }

    tree->root->color = Color::BLACK;
}

void insert(RBTree* tree, Node* new_node) {
    Node* parent = tree->nil;
    Node* current = tree->root;

    while (current != tree->nil) {
        parent = current;
        if (new_node->key < current->key) {
            current = current->left;
        } else {
            current = current->right;
        }
    }

    new_node->parent = parent;

    if (parent == tree->nil) {
        tree->root = new_node;
    } else if (new_node->key < parent->key) {
        parent->left = new_node;
    } else {
        parent->right = new_node;
    }

    new_node->left = tree->nil;
    new_node->right = tree->nil;
    new_node->color = Color::RED;

    insert_fixup(tree, new_node);
}

void preorder_traversal(const Node* node, const Node* nil, bool& is_first_node) {
    if (node == nil) {
        return;
    }

    if (!is_first_node) {
        cout << ", ";
    }

    cout << node->key << "(" << (node->color == Color::RED ? "R" : "B") << ")";
    is_first_node = false;

    preorder_traversal(node->left, nil, is_first_node);
    preorder_traversal(node->right, nil, is_first_node);
}

void build_tree(RBTree* tree, size_t node_count) {
    cout << "Provide " << node_count << " keys for the tree:" << endl;

    for (size_t i = 0; i < node_count; ++i) {
        int key_input;

        cout << "  Key #" << (i + 1) << ": ";
        cin >> key_input;

        insert(tree, create_node(tree, key_input));
    }

    cout << endl;
}

void handle_red_black_tree_workflow() {
    RBTree tree = create_tree();

    size_t node_count;
    cout << "Enter number of nodes: ";
    cin >> node_count;

    cout << endl;

    build_tree(&tree, node_count);

    cout << "Preorder traversal [key(color)]: ";

    bool is_first_node = true;
    preorder_traversal(tree.root, tree.nil, is_first_node);

    cout << "." << endl;

    destroy_tree(&tree);
}

int main() {
    handle_red_black_tree_workflow();
    return 0;
}
