import requests
import json
from datetime import datetime, timedelta


def get_all_orders(weeks=1):

    headers = {
        'Authorization': 'chave_api 32b19b99033db32ab955 aplicacao 120f779a-59dc-4351-92f6-857efd50362a'
    }

    qtd_orders = 0
    response = None
    while qtd_orders < 100:
        data_hora_atual = datetime.now()

        # Subtrai uma semana da data e hora atual
        uma_semana_atras = data_hora_atual - timedelta(weeks=weeks)

        # Formata a data e hora no formato desejado: AAAA-MM-DDTHH:MM:SS
        data_formatada = uma_semana_atras.strftime('%Y-%m-%dT%H:%M:%S')

        url = f"https://api.awsli.com.br/v1/pedido/search/?limit=50&since_criado={data_formatada}"

        responseDescoveryWeek = requests.request("GET", url, headers=headers).json()

        qtd_orders = int(responseDescoveryWeek.get("meta").get("total_count"))

        weeks += 1

        response = responseDescoveryWeek

    haveNext = response.get("meta").get("next")

    orders = []
    orders += response.get("objects")

    while haveNext:
        url = f"https://api.awsli.com.br" + haveNext
        responseMoreResults = requests.request("GET", url, headers=headers).json()
        orders += responseMoreResults.get("objects")
        haveNext = responseMoreResults.get("meta").get("next")

    new_orders = [
        {
            "resourceRoute": o.get("resource_uri"),
            "numeroPedido": o.get("numero"),
            "valor": o.get("valor_total"),
            "status": o.get("situacao").get("nome")
        }
        for o in orders
    ]

    return get_data_client(new_orders)

    # if qtd_orders < 100:
    #     get_all_orders(weeks + 1)
    # else:
    #
    #     orders = []
    #     haveNext = response.get("meta").get("next")
    #
    #     orders += response["objects"]
    #
    #     while haveNext:
    #         orders = response["objects"]
    #         url = f"https://api.awsli.com.br{haveNext}"
    #
    #         headers = {
    #             'Authorization': 'chave_api 32b19b99033db32ab955 aplicacao 120f779a-59dc-4351-92f6-857efd50362a'
    #         }
    #
    #         response = requests.request("GET", url, headers=headers).json()
    #         orders += response["objects"]
    #         haveNext = response.get("meta").get("next")
    #         print("list size:", len(orders))
    #
    #     new_orders = [
    #         {
    #             "resourceRoute": o.get("resource_uri"),
    #             "numeroPedido": o.get("numero"),
    #             "valor": o.get("valor_total"),
    #             "status": o.get("situacao").get("nome")
    #         }
    #         for o in orders
    #     ]
    #
    #     return get_data_client(new_orders)


def get_data_client(data_orders):
    for data_order in data_orders:
        url = f"https://api.awsli.com.br{data_order['resourceRoute']}"

        headers = {
            'Authorization': 'chave_api 32b19b99033db32ab955 aplicacao 120f779a-59dc-4351-92f6-857efd50362a'
        }

        response = requests.request("GET", url, headers=headers).json()

        envios = response.get("envios")

        if len(envios) > 1:
            isFirst = True
            for envio in envios:

                data_objeto = datetime.strptime(envio.get("data_modificacao"),
                                                "%Y-%m-%dT%H:%M:%S"
                                                ".%f")

                if envio.get("situacao").get("aprovado"):
                    data_formatada = data_objeto.strftime("%d/%m/%Y")
                else:
                    data_formatada = None

                if isFirst:
                    data_order.update({
                        "email": response.get("cliente").get("email"),
                        "nome": response.get("cliente").get("nome"),
                        "telefone": response.get("cliente").get("telefone_celular"),
                        "transportadora": envio.get("forma_envio").get("nome"),
                        "codigo_rastreio": envio.get("forma_envio").get("code"),
                        "prazo": envio.get("prazo"),
                        "data_pagamento": data_formatada
                    })
                    isFirst = False
                else:
                    data_order.append({
                        "email": response.get("cliente").get("email"),
                        "nome": response.get("cliente").get("nome"),
                        "telefone": response.get("cliente").get("telefone_celular"),
                        "transportadora": envio.get("forma_envio").get("nome"),
                        "codigo_rastreio": envio.get("forma_envio").get("code"),
                        "prazo": envio.get("prazo"),
                        "data_pagamento": data_formatada
                    })
        else:
            data_objeto = datetime.strptime(response.get("envios")[0].get("data_modificacao"), "%Y-%m-%dT%H:%M:%S"
                                                                                               ".%f")
            if response.get("situacao").get("aprovado"):
                data_formatada = data_objeto.strftime("%d/%m/%Y")
            else:
                data_formatada = None

            data_order.update({
                "email": response.get("cliente").get("email"),
                "nome": response.get("cliente").get("nome"),
                "telefone": response.get("cliente").get("telefone_celular"),
                "transportadora": response.get("envios")[0].get("forma_envio").get("nome"),
                "codigo_rastreio": response.get("envios")[0].get("forma_envio").get("code"),
                "prazo": response.get("envios")[0].get("prazo"),
                "data_pagamento": data_formatada
            })

    return data_orders


def update_order_status(order_id, status):
    url = f"https://api.awsli.com.br/v1/situacao/pedido/{order_id}"

    payload = json.dumps({
        "codigo": status
    })
    headers = {
        'Authorization': 'chave_api 32b19b99033db32ab955 aplicacao 120f779a-59dc-4351-92f6-857efd50362a',
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    # print(response.json())


responseResult = get_all_orders()
print(responseResult)
print("resultados", len(responseResult))
