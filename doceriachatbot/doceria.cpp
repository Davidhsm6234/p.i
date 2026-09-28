// doceria.cpp â€“ lÃ³gica do pedido (catÃ¡logo + carrinho) em C++
// Sem banco de dados: tudo fica em memÃ³ria (std::map).
//
// Compilar para WebAssembly (Emscripten):
//   emcc doceria.cpp -O2 -o doceria.js
//     -s EXPORTED_FUNCTIONS="['_cart_add','_cart_remove','_cart_qty','_cart_total','_cart_clear','_cart_summary','_price_of']"
//     -s EXPORTED_RUNTIME_METHODS="['ccall','cwrap','UTF8ToString']"
//   (tudo em uma linha sÃ³, no terminal)
//
// Teste nativo:  g++ -std=c++17 doceria.cpp -o doceria && ./doceria

#include <cstdio>
#include <map>
#include <string>

struct Produto { std::string nome; double preco; };

static const std::map<std::string, Produto> CATALOGO = {
    {"brigadeiro", {"Brigadeiro", 3.50}},
    {"beijinho",   {"Beijinho", 3.50}},
    {"brownie",    {"Brownie", 8.00}},
    {"cupcake",    {"Cupcake", 9.00}},
    {"torta",      {"Torta de limao (fatia)", 12.00}},
    {"cookie",     {"Cookie", 6.00}},
    {"bolo",       {"Bolo de pote", 10.00}},
};

static std::map<std::string, int> carrinho;  // chave -> quantidade
static std::string bufferResumo;             // mantÃ©m a string viva para o JS ler

extern "C" {

// PreÃ§o unitÃ¡rio (-1 se o produto nÃ£o existe)
double price_of(const char* chave) {
    auto it = CATALOGO.find(chave);
    return it == CATALOGO.end() ? -1.0 : it->second.preco;
}

// Adicionar produto + quantidade. Retorna a nova quantidade, ou -1 se invÃ¡lido.
int cart_add(const char* chave, int qtd) {
    if (qtd <= 0 || CATALOGO.find(chave) == CATALOGO.end()) return -1;
    carrinho[chave] += qtd;
    return carrinho[chave];
}

// Remove unidades; apaga o item se chegar a zero. Retorna a quantidade restante.
int cart_remove(const char* chave, int qtd) {
    auto it = carrinho.find(chave);
    if (it == carrinho.end() || qtd <= 0) return 0;
    it->second -= qtd;
    if (it->second <= 0) { carrinho.erase(it); return 0; }
    return it->second;
}

int cart_qty(const char* chave) {
    auto it = carrinho.find(chave);
    return it == carrinho.end() ? 0 : it->second;
}

double cart_total() {
    double total = 0;
    for (const auto& [chave, qtd] : carrinho) total += CATALOGO.at(chave).preco * qtd;
    return total;
}

void cart_clear() { carrinho.clear(); }

// Resumo em texto (ponteiro vÃ¡lido atÃ© a prÃ³xima chamada)
const char* cart_summary() {
    if (carrinho.empty()) { bufferResumo = "Seu carrinho esta vazio."; return bufferResumo.c_str(); }
    bufferResumo = "Seu pedido:\n";
    char linha[160];
    for (const auto& [chave, qtd] : carrinho) {
        const Produto& p = CATALOGO.at(chave);
        std::snprintf(linha, sizeof linha, "- %dx %s: R$ %.2f\n", qtd, p.nome.c_str(), p.preco * qtd);
        bufferResumo += linha;
    }
    std::snprintf(linha, sizeof linha, "Total: R$ %.2f", cart_total());
    bufferResumo += linha;
    return bufferResumo.c_str();
}

}  // extern "C"

// Teste rÃ¡pido fora do navegador
#ifndef __EMSCRIPTEN__
int main() {
    cart_add("brigadeiro", 6);
    cart_add("brownie", 2);
    cart_add("brigadeiro", 4);
    cart_remove("brownie", 1);
    std::printf("%s\n", cart_summary());
}
#endif