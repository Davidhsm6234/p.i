// app.js – interface e regras do chatbot.
// O carrinho (adicionar, remover, total, resumo) roda em C++ (doceria.cpp -> WebAssembly).
 
// Precisa existir ANTES do doceria.js carregar.
var Module = {
  onRuntimeInitialized: iniciar,
  onAbort: m => mostrarErro("O módulo C++ falhou ao carregar: " + m),
};
 
// A posição na lista = id do produto no C++ (mesma ordem do doceria.cpp).
const PRODUCTS = [
  { k: "brigadeiro", n: "Brigadeiro",             p: 3.5 },
  { k: "beijinho",   n: "Beijinho",               p: 3.5 },
  { k: "brownie",    n: "Brownie",                p: 8 },
  { k: "cupcake",    n: "Cupcake",                p: 9 },
  { k: "torta",      n: "Torta de limão (fatia)", p: 12 },
  { k: "cookie",     n: "Cookie",                 p: 6 },
  { k: "bolo",       n: "Bolo de pote",           p: 10 },
];
PRODUCTS.forEach((p, i) => p.id = i);
 
let cartAdd, cartRemove, cartQty, cartTotal, cartClear, cartSummary; // funções do C++
let pronto = false;
let pending = null; // produto aguardando quantidade
 
const $ = id => document.getElementById(id);
const brl = v => v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const norm = s => s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
 
function mostrarErro(msg) { say("⚠️ " + msg, "bot"); }
 
$("f").onsubmit = e => {
  e.preventDefault();
  const v = $("in").value;
  $("in").value = "";
  if (!pronto) return mostrarErro("O módulo C++ ainda não carregou. Confira se doceria.js e doceria.wasm foram publicados.");
  send(v);
};
 
setTimeout(() => {
  if (!pronto) mostrarErro("O módulo C++ não carregou. Abra o console do navegador (F12) para ver o erro.");
}, 4000);
 
function iniciar() {
  try {
    cartAdd     = Module.cwrap("cart_add",    "number", ["number", "number"]);
    cartRemove  = Module.cwrap("cart_remove", "number", ["number", "number"]);
    cartQty     = Module.cwrap("cart_qty",    "number", ["number"]);
    cartTotal   = Module.cwrap("cart_total",  "number", []);
    cartClear   = Module.cwrap("cart_clear",  null,     []);
    cartSummary = () => Module.UTF8ToString(Module._cart_summary());
    pronto = true;
 
    renderCart();
    say("Olá! 😊 Bem-vindo(a) à Juber Doces!\n" + menuText(), "bot");
    menuQuick();
  } catch (e) {
    mostrarErro("Erro ao iniciar: " + e.message);
  }
}
 
/* ---------- Interface ---------- */
function say(texto, quem) {
  const d = document.createElement("div");
  d.className = "m " + quem;
  d.textContent = texto;
  $("msgs").appendChild(d);
  $("msgs").scrollTop = 1e9;
}
 
function quick(opcoes) {
  const q = $("quick");
  q.innerHTML = "";
  opcoes.forEach(o => {
    const b = document.createElement("button");
    b.textContent = o;
    b.onclick = () => send(o);
    q.appendChild(b);
  });
}
 
function menuQuick() {
  quick(PRODUCTS.map(p => p.n.split(" (")[0]).concat(["Carrinho", "Finalizar"]));
}
 
function menuText() {
  return "Nosso cardápio:\n" + PRODUCTS.map(p => `• ${p.n} – ${brl(p.p)}`).join("\n") +
         "\n\nEscolha um produto ou escreva, por exemplo: 3 brownies.";
}
 
function renderCart() {
  const c = $("cart");
  c.innerHTML = "";
  let temItem = false;
 
  PRODUCTS.forEach(p => {
    const q = cartQty(p.id);               // <- C++
    if (q <= 0) return;
    temItem = true;
 
    const linha = document.createElement("div");
    linha.className = "it";
    linha.innerHTML = '<span class="n"></span><button>−</button><b>' + q + "</b><button>+</button>";
    linha.querySelector(".n").textContent = p.n;
    const [menos, mais] = linha.querySelectorAll("button");
    menos.onclick = () => { cartRemove(p.id, 1); renderCart(); };   // <- C++
    mais.onclick  = () => { cartAdd(p.id, 1);    renderCart(); };   // <- C++
    c.appendChild(linha);
  });
 
  if (!temItem) c.innerHTML = '<div class="empty">Nenhum item ainda.</div>';
  $("total").textContent = brl(cartTotal());   // <- C++
}
 
/* ---------- Regras do bot ---------- */
function adicionar(produto, qtd) {
  cartAdd(produto.id, qtd);                     // <- C++
  renderCart();
  say(`Adicionei ${qtd}x ${produto.n} ao pedido! 🎉\nQuer mais alguma coisa? Escolha outro produto ou diga "finalizar".`, "bot");
  menuQuick();
}
 
function temItens() { return cartTotal() > 0; }
 
function responder(raw) {
  const t = norm(raw);
  const num = (t.match(/\d+/) || [])[0];
  const qtd = num ? parseInt(num, 10) : null;
 
  if (/^(oi|ola|bom dia|boa tarde|boa noite)/.test(t) && !pending) {
    say("Olá! 😊 Bem-vindo(a) à Doceria da Vó!\n" + menuText(), "bot");
    return menuQuick();
  }
  if (/cardapio|menu|produtos/.test(t)) {
    pending = null;
    say(menuText(), "bot");
    return menuQuick();
  }
  if (/limpar|esvaziar|cancelar/.test(t)) {
    pending = null;
    cartClear();                               // <- C++
    renderCart();
    say("Pedido limpo. Podemos recomeçar! 🍰", "bot");
    return menuQuick();
  }
  if (/carrinho|pedido|resumo/.test(t) && !/finalizar/.test(t)) {
    return say(cartSummary(), "bot");          // <- C++
  }
  if (/finalizar|fechar|concluir/.test(t)) {
    pending = null;
    if (!temItens()) {
      say("Seu carrinho está vazio. Que tal escolher um docinho?", "bot");
      return menuQuick();
    }
    say(cartSummary() + "\n\nPedido registrado! Obrigado pela preferência 💖 (demonstração: nada é salvo).", "bot");
    return quick(["Novo pedido"]);
  }
  if (t === "novo pedido") {
    cartClear();
    renderCart();
    say("Vamos lá! O que vai ser hoje?", "bot");
    return menuQuick();
  }
 
  const achado = PRODUCTS.find(p => t.includes(p.k));
  if (achado) {
    if (qtd > 0) { pending = null; return adicionar(achado, qtd); }
    pending = achado;
    say(`Ótima escolha! Quantas unidades de ${achado.n} você quer?`, "bot");
    return quick(["1", "2", "4", "6", "12"]);
  }
  if (pending && qtd > 0) {
    const p = pending;
    pending = null;
    return adicionar(p, qtd);
  }
  if (pending) {
    say(`Não entendi a quantidade. Digite um número para ${pending.n}.`, "bot");
    return quick(["1", "2", "4", "6", "12"]);
  }
  say('Não entendi 🤔 Escolha um produto do cardápio, ou diga "carrinho" ou "finalizar".', "bot");
  menuQuick();
}
 
function send(texto) {
  if (!texto.trim()) return;
  say(texto, "me");
  setTimeout(() => responder(texto), 250);
}
 
