import requests
from time import sleep


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
                listProducts = verifyAddedInListProdutos(
                    listProducts,
                    product
                )
        else:
            product = {
                "nomeProduto": itens[0].get('nome'),
                "quantidade": int(itens[0].get('quantidade').replace('.', '')),
                "valor": itens[0].get('preco_venda')
            }
            listProducts = verifyAddedInListProdutos(
                listProducts,
                product
            )
    return listProducts


def list_more_sells(dataInicial, dataFinal, token):
    url = f"https://www.bling.com.br/Api/v3/nfe?dataEmissaoInicial={dataInicial}&dataEmissaoFinal={dataFinal}"

    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Cookie': 'PHPSESSID=1a06ulj1eh9g3arn5hqjlsn8gq'
    }

    notasFiscais = requests.request("GET", url, headers=headers, data=payload).json().get('data')

    idsPedidos = []

    for notaFiscal in notasFiscais:
        url = f"https://www.bling.com.br/Api/v3/pedidos/vendas?numero={notaFiscal.get('numero')}"

        response = requests.request("GET", url, headers=headers, data=payload)

        idPedido = response.json().get('data')[0].get('id')

        sleep(3)

        idsPedidos.append(
            idPedido
        )

    listProdutos = []
    for idPedido in idsPedidos:
        url = f"https://www.bling.com.br/Api/v3/pedidos/vendas/{idPedido}"

        response = requests.request("GET", url, headers=headers, data=payload).json().get('data')
        sleep(3)
        for item in response.get('itens'):

            # faça um switch
            idloja = str(response.get('loja').get('id'))
            canal_de_venda = idloja
            if idloja == "203768813":
                canal_de_venda = 'Site'
            elif idloja == "204527966":
                canal_de_venda = 'Shopee'
            elif idloja == '204525390':
                canal_de_venda = 'Mercado Livre'
            elif idloja == '203890758':
                canal_de_venda = 'Carrefour'
            elif idloja == '204540954':
                canal_de_venda = 'B2W'

            produto = {
                "nomeProduto": item.get('descricao'),
                "quantidade": item.get('quantidade'),
                "valor": item.get('comissao').get('base'),
                "canalVenda": canal_de_venda
            }

            listProdutos = verifyAddedInListProdutos(listProdutos, produto)

    return listProdutos


def verifyAddedInListProdutos(listProducts, product):
    inList = False
    for i in listProducts:
        if i.get('nomeProduto') == product.get('nomeProduto'):
            i['quantidade'] += product.get('quantidade')
            i['valor'] += product.get('valor')
            inList = True
            break

    if not inList:
        listProducts.append(product)

    return listProducts


print(list_more_sells("10/10/2023", "11/10/2023", '56603fac80af3d525d69d5cab7ae2c081df9b4a7'))
