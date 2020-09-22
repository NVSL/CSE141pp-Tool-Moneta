#include <iostream>
#include <fstream>
#include <regex>


constexpr int ALPHABET_SIZE = 26;

struct Node {
  bool end_node {false};
  char letter;
  Node* children [ALPHABET_SIZE] = {0};

  Node() : letter {0} {}

  Node(char c) : letter {c} {}

  ~Node() {
    for (Node * child: children) delete child;
  }
};

class Trie {
public:
  int count;
  Node root_node;
  Trie() : count {0}, root_node {} {} // or root_node(new Node())

  bool insert_word(std::string word) {
    Node* curr_node = &root_node;
    for (char c : word) {
      if (curr_node->children[c-'a'] == nullptr) {
        curr_node->children[c-'a'] = new Node(c);
      }
      curr_node = curr_node->children[c-'a'];
    }
    if (curr_node->end_node) {
      return false;
    }
    count++;
    curr_node->end_node = true;
    return true;
  }

  bool has_word(std::string word) {
    Node* curr_node = &root_node;
    for (char c : word) {
      curr_node = curr_node->children[c-'a'];
      if (curr_node == nullptr) {
        return false;
      }
    }
    return curr_node->end_node;
  }
};

int main(int argc, char *argv[]) {
  std::ifstream infile {"words.txt"};
  std::regex regexp("[\\W0-9A-Z_]+"); // only a-z allowed
  std::string line;
  Trie t;
  while (std::getline(infile, line)) {
    line = std::regex_replace(line, regexp, "");
    t.insert_word(line);
  }
  std::string test_list [] = {
    "adjustment", "actor", "anticipate",
    "background", "boundary", "beginning",
    "city", "coalition", "constitutional",
    "transformation", "twice", "tournament",
    "understand", "ultimate", "user",
    "vegetable", "virtue", "vote"};
  int count = 0;
  for (std::string test_word: test_list) {
    bool in_trie = t.has_word(test_word);
    if (!in_trie) {
      count++;
    }
  }
  if (count != 0) {
    std::cerr << "Trie failed to find a word. How many? " << count << "\n";
  }
  count = 0;
  for (std::string test_word: test_list) {
    bool in_trie = t.has_word(test_word + "z");
    if (in_trie) {
      count++;
    }
  }
  if (count != 0) {
    std::cerr << "Trie found a missing word. How many? " << count << "\n";
  }
  return 0;
}
