import requests


def get_datas(dataInicial, dataFinal):
    url = f"https://api.awsli.com.br/v1/pedido/search/?since_criado={dataInicial}&until_criado={dataFinal}"

    headers = {
        'Authorization': 'chave_api 32b19b99033db32ab955 aplicacao 120f779a-59dc-4351-92f6-857efd50362a'
    }

    response = requests.request("GET", url, headers=headers).json()

    ordersUtils = response.get("objects")
    nextOrders = response.get('meta').get('next')

    while nextOrders:
        url = f"https://api.awsli.com.br{nextOrders}"

        responseMoreOrders = requests.request("GET", url, headers=headers).json()

        ordersUtils += responseMoreOrders.get('objects')
        nextOrders = responseMoreOrders.get('meta').get('next')

    orderClean = []

    srcs = []
    for order in ordersUtils:
        if order.get('situacao').get('aprovado'):
            srcs.append(order.get('resource_uri'))

    for src in srcs:
        url = f"https://api.awsli.com.br{src}"

        responseSrc = requests.request("GET", url, headers=headers).json()

        itens = responseSrc.get('itens')

        if len(itens) > 1:
            for item in itens:
                client = {
                    "telefone": responseSrc.get('cliente').get('telefone_celular'),
                    "nomeCliente": responseSrc.get('cliente').get('nome'),
                    "email": responseSrc.get('cliente').get('email'),
                    "quatidadeCompras": int(item.get('quantidade').replace(".", "")),
                    "valores": responseSrc.get('pagamentos')[0].get('valor_pago')
                }
                orderClean = verifyAddedInListClients(orderClean, client)
        else:
            client = {
                "telefone": responseSrc.get('cliente').get('telefone_celular'),
                "nomeCliente": responseSrc.get('cliente').get('nome'),
                "email": responseSrc.get('cliente').get('email'),
                "quatidadeCompras": int(itens[0].get('quantidade').replace('.', '')),
                "valores": responseSrc.get('pagamentos')[0].get('valor_pago')
            }

            orderClean = verifyAddedInListClients(orderClean, client)

    return sorted(orderClean, key=lambda x: x.get('quatidadeCompras'), reverse=True)


def verifyAddedInListClients(listClients, clients):
    inList = False
    for i in listClients:
        if i.get('nomeCliente') == clients.get('nomeCliente'):
            i['quatidadeCompras'] += clients.get('quatidadeCompras')
            inList = True
            break

    if not inList:
        listClients.append(clients)

    return listClients


def get_data_product(dataInicial, dataFinal):
    url = f"https://api.awsli.com.br/v1/pedido/search/?since_criado={dataInicial}&until_criado={dataFinal}"

    headers = {
        'Authorization': 'chave_api 32b19b99033db32ab955 aplicacao 120f779a-59dc-4351-92f6-857efd50362a'
    }

    response = requests.request("GET", url, headers=headers).json()

    ordersUtils = response.get("objects")
    nextOrders = response.get('meta').get('next')

    while nextOrders:
        url = f"https://api.awsli.com.br{nextOrders}"

        responseMoreOrders = requests.request("GET", url, headers=headers).json()

        ordersUtils += responseMoreOrders.get('objects')
        nextOrders = responseMoreOrders.get('meta').get('next')

    listProducts = []

    srcs = []
    for order in ordersUtils:
        if order.get('situacao').get('aprovado'):
            srcs.append(order.get('resource_uri'))

    for src in srcs:
        url = f"https://api.awsli.com.br{src}"

        responseSrc = requests.request("GET", url, headers=headers).json()

        itens = responseSrc.get('itens')

        if len(itens) > 1:
            for item in itens:
                product = {
                    "nomeProduto": item.get('nome'),
                    "quantidade": int(item.get('quantidade').replace('.', '')),
                    "valor": item.get('preco_venda')
                }
                listProducts = verifyAddedInList(
                    listProducts,
                    product
                )
        else:
            product = {
                "nomeProduto": itens[0].get('nome'),
                "quantidade": int(itens[0].get('quantidade').replace('.', '')),
                "valor": itens[0].get('preco_venda')
            }
            listProducts = verifyAddedInList(
                listProducts,
                product
            )
    return listProducts


def verifyAddedInList(listProducts, product):
    inList = False
    for i in listProducts:
        if i.get('nomeProduto') == product.get('nomeProduto'):
            i['quantidade'] += product.get('quantidade')
            inList = True
            break

    if not inList:
        listProducts.append(product)

    return listProducts


print(get_datas("2023-10-1", "2023-10-11"))
