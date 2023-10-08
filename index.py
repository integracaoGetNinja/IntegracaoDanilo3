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
from flask import Flask, jsonify
import threading
from utils import apiLIUtils

app = Flask(__name__)


def rota_demorada():
    try:
        # Define um limite de tempo para a função demorada (10 segundos neste caso)
        resultado = apiLIUtils.get_all_orders()
        return jsonify(resultado)
    except TimeoutError as e:
        return jsonify(error=str(e)), 500


@app.route("/atualizar_base")
def atualizar_base():
    return run_with_timeout()


def run_with_timeout():
    timeout = 120  # Defina o tempo limite em segundos
    thread = threading.Thread(target=rota_demorada)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        thread._stop()  # Para a execução da thread se estiver demorando demais
        return jsonify(error="A operação demorada excedeu o tempo limite."), 500
    return rota_demorada()


if __name__ == "__main__":
    app.run()
