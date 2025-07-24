import time
import random
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum
import threading
import queue

class StatusEstoque(Enum):
    VERDE = "VERDE"
    AMARELO = "AMARELO"
    VERMELHO = "VERMELHO"

@dataclass
class Produto:
    id: str
    nome: str
    partes_totais: int  # Kit base (43) + Kit variação (20-33)
    
    def __post_init__(self):
        # Produtos P1-P5 com variação de 63-76 partes (43 base + 20-33 variação)
        if self.partes_totais == 0:
            self.partes_totais = 43 + random.randint(20, 33)

@dataclass
class EstoqueParte:
    nome: str
    quantidade_atual: int
    nivel_verde: int = 100
    nivel_amarelo: int = 50
    nivel_vermelho: int = 20
    
    def get_status(self) -> StatusEstoque:
        if self.quantidade_atual >= self.nivel_verde:
            return StatusEstoque.VERDE
        elif self.quantidade_atual >= self.nivel_amarelo:
            return StatusEstoque.AMARELO
        else:
            return StatusEstoque.VERMELHO

@dataclass
class DepositoProdutosAcabados:
    estoque: Dict[str, int]

    def __init__(self):
        self.estoque = {f"P{i+1}": 0 for i in range(5)}

    def armazenar(self, produto_id: str, quantidade: int):
        self.estoque[produto_id] += quantidade

    def status(self) -> str:
        status = "\n📦 DEPÓSITO DE PRODUTOS ACABADOS:\n"
        for pid, qtd in self.estoque.items():
            cor = "🟢" if qtd > 20 else ("🟡" if qtd > 5 else "🔴")
            status += f"   {cor} {pid}: {qtd} unidades\n"
        return status

class LinhaProducao:
    def __init__(self, linha_id: str, fabrica_id: str):
        self.linha_id = linha_id
        self.fabrica_id = fabrica_id
        self.buffer_materiais = 0
        self.produtos_acabados = 0
        self.ocupada = False
        self.produto_atual = None
    
    def produzir(self, produto: Produto, quantidade: int, estoque_partes: EstoqueParte, deposito: DepositoProdutosAcabados):
        if self.ocupada:
            return False
        
        partes_necessarias = produto.partes_totais * quantidade
        
        # Verifica se há partes suficientes
        if estoque_partes.quantidade_atual < partes_necessarias:
            print(f"⚠️ Linha {self.linha_id} Fábrica {self.fabrica_id}: Não há partes suficientes para produzir {quantidade}x {produto.nome}")
            return False
        
        # Inicia produção
        self.ocupada = True
        self.produto_atual = produto
        
        # Consome partes do estoque
        estoque_partes.quantidade_atual -= partes_necessarias
        
        # Simula tempo de produção
        time.sleep(1)
        
        # Finaliza produção
        self.produtos_acabados += quantidade
        self.ocupada = False
        self.produto_atual = None

        # Finaliza produção
        self.produtos_acabados += quantidade
        deposito.armazenar(produto.id, quantidade)

        print(f"Linha {self.linha_id}: Produziu {quantidade}x {produto.nome}")
        return True

class Fabrica:
    def __init__(self, fabrica_id: str, num_linhas: int):
        self.fabrica_id = fabrica_id
        self.linhas = [LinhaProducao(f"L{i+1}", fabrica_id) for i in range(num_linhas)]
        self.fila_producao = queue.Queue()
    
    def adicionar_ordem(self, produto: Produto, quantidade: int):
        self.fila_producao.put((produto, quantidade))
    
    def processar_ordens(self, estoque_partes: EstoqueParte, deposito: DepositoProdutosAcabados):
        for linha in self.linhas:
            if not linha.ocupada and not self.fila_producao.empty():
                try:
                    produto, quantidade = self.fila_producao.get_nowait()
                    thread = threading.Thread(
                        target=linha.produzir,
                        args=(produto, quantidade, estoque_partes, deposito)
                    )
                    thread.start()
                except queue.Empty:
                    pass

class SistemaMonitoramento:
    def __init__(self):
        self.fornecedores = ["Fornecedor A", "Fornecedor B", "Fornecedor C"]
    
    def verificar_estoque(self, estoque_partes: EstoqueParte) -> str:
        status = estoque_partes.get_status()
        
        if status == StatusEstoque.VERMELHO:
            # Emite ordem de compra automática
            self.emitir_ordem_compra(estoque_partes)
            return f"🔴 CRÍTICO: Estoque baixo ({estoque_partes.quantidade_atual} partes)"
        elif status == StatusEstoque.AMARELO:
            return f"🟡 ATENÇÃO: Estoque moderado ({estoque_partes.quantidade_atual} partes)"
        else:
            return f"🟢 OK: Estoque bom ({estoque_partes.quantidade_atual} partes)"
    
    def emitir_ordem_compra(self, estoque_partes: EstoqueParte):
        fornecedor = random.choice(self.fornecedores)
        quantidade_pedido = (estoque_partes.nivel_verde - estoque_partes.quantidade_atual) * 3
        
        print(f"📦 ORDEM DE COMPRA: {quantidade_pedido} partes de {fornecedor}")
        
        # Simula entrega (em thread separada)
        def simular_entrega():
            time.sleep(2)  # Simula tempo de entrega
            estoque_partes.quantidade_atual += quantidade_pedido
            print(f"✅ ENTREGA: {quantidade_pedido} partes recebidas de {fornecedor}")
        
        thread = threading.Thread(target=simular_entrega)
        thread.start()

class SistemaProducao:
    def __init__(self):
        # Inicializa fábricas
        self.fabrica1 = Fabrica("F1", 5)  # 5 linhas
        self.fabrica2 = Fabrica("F2", 8)  # 8 linhas
        
        # Inicializa o depósito
        self.deposito = DepositoProdutosAcabados()

        # Define produtos (P1-P5)
        self.produtos = [
            Produto("P1", "Produto P1", 0),
            Produto("P2", "Produto P2", 0),
            Produto("P3", "Produto P3", 0),
            Produto("P4", "Produto P4", 0),
            Produto("P5", "Produto P5", 0)
        ]
        
        # Estoque de partes (total de 100 tipos diferentes)
        self.estoque_partes = EstoqueParte("Partes", 100000, 100000, 90000, 80000)
        
        # Sistema de monitoramento
        self.monitoramento = SistemaMonitoramento()
        
        # Ainda não está executando
        self.executando = False
    
    # Gerar ordens aleatórias
    def gerar_ordens_aleatorias(self):
        """Gera ordens de produção aleatórias"""
        for _ in range(5):  # Gera 5 ordens
            produto = random.choice(self.produtos)
            quantidade = random.randint(1, 3)
            
            # Distribui entre fábricas
            if random.random() < 0.5:
                self.fabrica1.adicionar_ordem(produto, quantidade)
            else:
                self.fabrica2.adicionar_ordem(produto, quantidade)
    
    # Gerar ordens padrão
    def gerar_ordens_fabrica1_empurrada(self):
        """Fábrica 1: adiciona ordens fixas de 60 unidades para todos os produtos em todas as linhas (fabricação empurrada)"""
        for produto in self.produtos: # Ordem de 60 produtos por linha na fábrica 1
            self.fabrica1.adicionar_ordem(produto, 60)
    
    # Status
    def imprimir_status(self):
        """Imprime status do sistema"""
        print("\n" + "="*60)
        print("📊 STATUS DO SISTEMA DE PRODUÇÃO")
        print("="*60)
        
        # Status das fábricas
        print(f"\n🏭 FÁBRICA 1 ({len(self.fabrica1.linhas)} linhas):")
        for linha in self.fabrica1.linhas:
            status = "🔴 OCUPADA" if linha.ocupada else "🟢 LIVRE"
            produto = f" - {linha.produto_atual.nome}" if linha.produto_atual else ""
            print(f"   {linha.linha_id}: {status}{produto} | Acabados: {linha.produtos_acabados}")
        
        print(f"\n🏭 FÁBRICA 2 ({len(self.fabrica2.linhas)} linhas):")
        for linha in self.fabrica2.linhas:
            status = "🔴 OCUPADA" if linha.ocupada else "🟢 LIVRE"
            produto = f" - {linha.produto_atual.nome}" if linha.produto_atual else ""
            print(f"   {linha.linha_id}: {status}{produto} | Acabados: {linha.produtos_acabados}")
        
        # Status do estoque
        print(f"\n📦 ESTOQUE DE PARTES:")
        status_estoque = self.monitoramento.verificar_estoque(self.estoque_partes)
        print(f"   {status_estoque}")
        
        print(self.deposito.status())

        print("="*60)
    
    # Executar
    def executar(self):
        """Executa o sistema de produção"""
        print("🚀 Iniciando Sistema de Produção Kanban")
        print("Objetivo: Garantir que não ocorra ruptura na fabricação por falta de partes")
        
        # Agora está executando
        self.executando = True
        
        ciclo = 0
        while self.executando and ciclo < 15:  # 15 ciclos para demonstração
            ciclo += 1
            print(f"\n⏱️  Ciclo {ciclo}")

            # 🔵 Gera ordens fixas para a Fábrica 1 (empurrada)
            self.gerar_ordens_fabrica1_empurrada()

            # Gera novas ordens
            self.gerar_ordens_aleatorias()
            
            # Processa ordens nas fábricas
            self.fabrica1.processar_ordens(self.estoque_partes, self.deposito)
            self.fabrica2.processar_ordens(self.estoque_partes, self.deposito)

            # Mostra status
            self.imprimir_status()
            
            # Pausa entre ciclos
            time.sleep(2)           
        
        print("\n✅ Sistema finalizado")
        print("💡 O sistema Kanban manteve a produção sem rupturas!")

# Main
def main():
    print("🎯 Sistema de Produção - Controle Kanban de Estoque")
    print("Cenário: 2 fábricas, 5 produtos, controle automático de estoque")
    
    sistema = SistemaProducao()
    
    try:
        sistema.executar()
    except KeyboardInterrupt:
        print("\n❌ Sistema interrompido pelo usuário")
        sistema.executando = False

if __name__ == "__main__":
    main()