#include "../../pin_tags.h"
#include <iostream>
#include <random>
#include <cassert>
#include <limits>

constexpr int LIST_SIZE {100};
constexpr double LowerBound {0};
constexpr double UpperBound {1000};

std::uniform_real_distribution<float> unif {LowerBound, UpperBound};
std::default_random_engine re;

std::pair<const void*, const void*> list_limits;
struct Node {
  float val;
  Node* next;
  Node (float val, Node* next) : val(val), next(next) { }
};

int count_nodes(const Node* head) {
  int count = 0;
  while (head) {
    head = head->next;
    count++;
  }
  return count;
}

// Find minimum and maximum address of linked list
std::pair<const void*, const void*> min_max(const Node* head) {
  const void* min_addr = (void *)std::numeric_limits<long>::max();
  const void* max_addr = 0;
  while (head) {
    if (head < min_addr) {
      min_addr = head;
    }
    if (head > max_addr) {
      max_addr = head;
    }
    head = head->next;
  }
  max_addr = (char *)max_addr + sizeof(Node) - 1;
  return {min_addr, max_addr};
}

Node* init_list() {
  Node* head = new Node(unif(re), nullptr);
  Node* ret_head = head;
  for (int i = 1; i < LIST_SIZE; i++) {
    head->next = new Node(unif(re), nullptr);
    head = head->next;
  }
  return ret_head;
}

void free_list(Node* head) {
  while (head) {
    Node* next = head->next;
    delete head;
    head = next;
  }
}

bool verify_order(Node* head) {
  while (head) {
    Node* next = head->next;
    if (next && head->val > next->val) {
      return false;
    }
    head = next;
  }
  return true;
}

void swap(Node* const a, Node* const b) {
  float tmp = a->val;
  a->val = b->val;
  b->val = tmp;
}

void bubble_sort(Node** head, bool pointer) {
  Node* m_head = *head;
  int unsorted = LIST_SIZE;
  int i = 0;
  while (unsorted != 1) {
    int last_swap = 1;
    Node* prev = nullptr;
    std::string s = "Per loop " + std::to_string(i);
    DUMP_START(s.c_str(), list_limits.first, list_limits.second, true); // true since multiple bubble_sort()'s are called
    for (int j = 1; j < unsorted; j++) {
      if (m_head->val > m_head->next->val) {
        if (pointer) {
          if (m_head == *head) {
            *head = m_head->next;
            m_head->next = m_head->next->next;
            (*head)->next = m_head;
            m_head = *head;
          } else {
            prev->next = m_head->next;
            m_head->next = m_head->next->next;
            prev->next->next = m_head;
            m_head = prev->next;
          }
        } else {
          swap(m_head, m_head->next);
        }
        last_swap = j;
      }
      prev = m_head;
      m_head = m_head->next;
    }
    DUMP_STOP(s.c_str());
    i++;
    unsorted = last_swap;
    m_head = *head;
  }
}

int main() {
  std::cerr << "Initializing list\n";
  Node* head = init_list();
  list_limits = min_max(head);
  
  std::cerr << "Check number of nodes\n";
  DUMP_START("Count nodes", list_limits.first, list_limits.second, false);
  assert(LIST_SIZE == count_nodes(head));
  DUMP_STOP("Count nodes");

  std::cerr << "Bubble sort\n";
  DUMP_START("Before verify", list_limits.first, list_limits.second, false);
  std::cerr << "Sorted: " << (verify_order(head) ? "true" : "false") << "\n";
  DUMP_STOP("Before verify");
  DUMP_START("Bubble sort pointer", list_limits.first, list_limits.second, false);
  bubble_sort(&head, true);
  DUMP_STOP("Bubble sort pointer");
  DUMP_START("After verify", list_limits.first, list_limits.second, false);
  std::cerr << "Sorted: " << (verify_order(head) ? "true" : "false") << "\n";
  DUMP_STOP("After verify");
  DUMP_START("Count nodes", list_limits.first, list_limits.second, false); // false so gets added to previous Count nodes tag
  assert(LIST_SIZE == count_nodes(head));
  DUMP_STOP("Count nodes");

  DUMP_START("Free List", list_limits.first, list_limits.second, false);
  free_list(head);
  DUMP_STOP("Free List");


  std::cerr << "Initializing list again\n";
  head = init_list();
  list_limits = min_max(head);
  
  std::cerr << "Check number of nodes\n";
  DUMP_START("Count nodes2", list_limits.first, list_limits.second, false);
  assert(LIST_SIZE == count_nodes(head));
  DUMP_STOP("Count nodes2");

  std::cerr << "Bubble sort\n";
  DUMP_START("Before verify2", list_limits.first, list_limits.second, false);
  std::cerr << "Sorted: " << (verify_order(head) ? "true" : "false") << "\n";
  DUMP_STOP("Before verify2");
  DUMP_START("Bubble sort in place", list_limits.first, list_limits.second, false);
  bubble_sort(&head, false);
  DUMP_STOP("Bubble sort in place");
  DUMP_START("After verify2", list_limits.first, list_limits.second, false);
  std::cerr << "Sorted: " << (verify_order(head) ? "true" : "false") << "\n";
  DUMP_STOP("After verify2");
  DUMP_START("Count nodes2", list_limits.first, list_limits.second, false);
  assert(LIST_SIZE == count_nodes(head));
  DUMP_STOP("Count nodes2");

  DUMP_START("Free List2", list_limits.first, list_limits.second, false);
  free_list(head);
  DUMP_STOP("Free List2");

  return 0;
}


