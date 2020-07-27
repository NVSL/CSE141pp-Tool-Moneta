int recur(int p) {
  int *x = new int[p*10];
  return (p == 1) ? p : recur(p-1)+1;
}
int main() {
  int a = recur(100000);
  return 0;
}
