// doceria.cpp – lógica do pedido (catálogo + carrinho) em C++
// Sem banco de dados: tudo fica em memória.
// Os produtos são identificados por número (0, 1, 2...) para simplificar a ligação com o JavaScript.
//
// Compilar para WebAssembly (use em++, pois é C++), tudo em uma linha:
//   em++ doceria.cpp -O2 -o doceria.js -s EXPORTED_FUNCTIONS="['_cart_add','_cart_remove','_cart_qty','_cart_total','_cart_clear','_cart_summary','_price_of']" -s EXPORTED_RUNTIME_METHODS="['ccall','cwrap','UTF8ToString']"
//
// Teste nativo:  g++ -std=c++17 doceria.cpp -o doceria && ./doceria
 
#include <cstdio>
#include <string>
#include <vector>
 
struct Produto { const char* nome; double preco; };
 
// A posição na lista é o "id" do produto (mesma ordem do app.js)
static const std::vector<Produto> CATALOGO = {
    {"Brigadeiro", 3.50},
    {"Beijinho", 3.50},
    {"Brownie", 8.00},
    {"Cupcake", 9.00},
    {"Torta de limão (fatia)", 12.00},
    {"Cookie", 6.00},
    {"Bolo de pote", 10.00},
};
 
static std::vector<int> carrinho(CATALOGO.size(), 0);  // quantidade de cada produto
static std::string bufferResumo;                       // mantém o texto vivo para o JS ler
 
static bool valido(int id) { return id >= 0 && id < (int)CATALOGO.size(); }
 
extern "C" {
 
double price_of(int id) { return valido(id) ? CATALOGO[id].preco : -1.0; }
 
// Adicionar produto + quantidade. Retorna a nova quantidade, ou -1 se inválido.
int cart_add(int id, int qtd) {
    if (!valido(id) || qtd <= 0) return -1;
    carrinho[id] += qtd;
    return carrinho[id];
}
 
// Remove unidades (nunca fica abaixo de zero). Retorna a quantidade restante.
int cart_remove(int id, int qtd) {
    if (!valido(id) || qtd <= 0) return 0;
    carrinho[id] -= qtd;
    if (carrinho[id] < 0) carrinho[id] = 0;
    return carrinho[id];
}
 
int cart_qty(int id) { return valido(id) ? carrinho[id] : 0; }
 
double cart_total() {
    double total = 0;
    for (size_t i = 0; i < CATALOGO.size(); i++) total += CATALOGO[i].preco * carrinho[i];
    return total;
}
 
void cart_clear() { for (int& q : carrinho) q = 0; }
 
const char* cart_summary() {
    bufferResumo = "";
    char linha[160];
    for (size_t i = 0; i < CATALOGO.size(); i++) {
        if (carrinho[i] <= 0) continue;
        std::snprintf(linha, sizeof linha, "• %dx %s – R$ %.2f\n", carrinho[i], CATALOGO[i].nome, CATALOGO[i].preco * carrinho[i]);
        bufferResumo += linha;
    }
    if (bufferResumo.empty()) return "Seu carrinho está vazio.";
    bufferResumo = "Seu pedido:\n" + bufferResumo;
    std::snprintf(linha, sizeof linha, "Total: R$ %.2f", cart_total());
    bufferResumo += linha;
    return bufferResumo.c_str();
}
 
}  // extern "C"
 
#ifndef __EMSCRIPTEN__
int main() {
    cart_add(0, 6); cart_add(2, 2); cart_add(0, 4); cart_remove(2, 1);
    std::printf("%s\n", cart_summary());
}
#endif
 
