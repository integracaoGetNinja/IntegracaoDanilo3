"""
    # Demanda 1
    # atualizar o Status de envio dos pedidos.
    # 100 últimas transações,fazer um parâmetro na planilha
    # Status
    # Código de Rastreamento
    # Número de Pedido
    # Nome do Cliente
    # Celular
    # E-mail
    # Valor
    # Transportadora
    # Data de Pagamento
    # Dias de Entrega

    pedido_pago
    pedido_em_separacao
    pronto_para_retirada
    aguardando_pagamento
    pagamento_devolvido
    pagamento_em_analise
    pedido_enviado
    pedido_entregue

    em_producao
    pedido_chargeback
    pagamento_em_disputa
    pedido_cancelado
    pedido_efetuado

"""
from flask import Flask, request, jsonify
from utils import apiLIUtils

app = Flask(__name__)


@app.route("/atualizar_base")
def atualizar_base():
    return jsonify(apiLIUtils.get_all_orders())


if __name__ == "__main__":
    app.run()
