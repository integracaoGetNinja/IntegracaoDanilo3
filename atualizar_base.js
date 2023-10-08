function getAllOrders(weeks) {
    var headers = {
        'Authorization': 'chave_api 32b19b99033db32ab955 aplicacao 120f779a-59dc-4351-92f6-857efd50362a'
    };

    var qtdOrders = 0;
    var response = null;
    var weekCount = weeks;

    while (qtdOrders < 100) {
        var dataHoraAtual = new Date();
        var umaSemanaAtras = new Date(dataHoraAtual.getTime() - (weekCount * 7 * 24 * 60 * 60 * 1000));

        var dataFormatada = umaSemanaAtras.toISOString();

        var url = 'https://api.awsli.com.br/v1/pedido/search/?limit=50&since_criado=' + dataFormatada;

        var responseDescoveryWeek = UrlFetchApp.fetch(url, {
            'headers': headers,
            'method': 'get'
        });

        var responseData = JSON.parse(responseDescoveryWeek.getContentText());
        qtdOrders = responseData.meta.total_count;
        weekCount++;
        response = responseData;
    }

    var haveNext = response.meta.next;
    var orders = response.objects;

    while (haveNext) {
        var responseMoreResults = UrlFetchApp.fetch('https://api.awsli.com.br' + haveNext, {
            'headers': headers,
            'method': 'get'
        });
        var responseMoreData = JSON.parse(responseMoreResults.getContentText());
        orders = orders.concat(responseMoreData.objects);
        haveNext = responseMoreData.meta.next;
    }

    var newOrders = orders.map(function(o) {
        return {
            'resourceRoute': o.resource_uri,
            'numeroPedido': o.numero,
            'valor': o.valor_total,
            'status': o.situacao.codigo
        };
    });

    return getDataClient(newOrders);
}

function getDataClient(dataOrders) {
    var updatedDataOrders = [];

    dataOrders.forEach(function(dataOrder) {
        var url = 'https://api.awsli.com.br' + dataOrder.resourceRoute;
        var headers = {
            'Authorization': 'chave_api 32b19b99033db32ab955 aplicacao 120f779a-59dc-4351-92f6-857efd50362a'
        };

        var response = UrlFetchApp.fetch(url, {
            'headers': headers,
            'method': 'get'
        });

        var responseData = JSON.parse(response.getContentText());
        var envios = responseData.envios;

        if (envios.length > 1) {
            var isFirst = true;

            envios.forEach(function(envio) {
                var dataObjeto = new Date(envio.data_modificacao);
                var dataFormatada = null;

                if (envio.situacao.aprovado) {
                    dataFormatada = Utilities.formatDate(dataObjeto, 'GMT', 'dd/MM/yyyy');
                }

                if (isFirst) {
                    dataOrder.email = responseData.cliente.email;
                    dataOrder.nome = responseData.cliente.nome;
                    dataOrder.telefone = responseData.cliente.telefone_celular;
                    dataOrder.transportadora = envio.forma_envio.nome;
                    dataOrder.codigo_rastreio = envio.forma_envio.code;
                    dataOrder.prazo = envio.prazo;
                    dataOrder.data_pagamento = dataFormatada;
                    isFirst = false;
                } else {
                    updatedDataOrders.push({
                        'email': responseData.cliente.email,
                        'nome': responseData.cliente.nome,
                        'telefone': responseData.cliente.telefone_celular,
                        'transportadora': envio.forma_envio.nome,
                        'codigo_rastreio': envio.forma_envio.code,
                        'prazo': envio.prazo,
                        'data_pagamento': dataFormatada
                    });
                }
            });
        } else {
            var firstEnvio = responseData.envios[0];

            var firstEnvioDataObjeto = new Date(firstEnvio.data_modificacao);
            var firstEnvioDataFormatada = null;

            if (responseData.situacao.aprovado) {
                firstEnvioDataFormatada = Utilities.formatDate(firstEnvioDataObjeto, 'GMT', 'dd/MM/yyyy');
            }

            dataOrder.email = responseData.cliente.email;
            dataOrder.nome = responseData.cliente.nome;
            dataOrder.telefone = responseData.cliente.telefone_celular;
            dataOrder.transportadora = firstEnvio.forma_envio.nome;
            dataOrder.codigo_rastreio = firstEnvio.forma_envio.code;
            dataOrder.prazo = firstEnvio.prazo;
            dataOrder.data_pagamento = firstEnvioDataFormatada;
        }

        updatedDataOrders.push(dataOrder);
    });

    return updatedDataOrders;
}


function atualizar_base(){

  var linha = 8;
  var col_status = 2;
  var col_cd_rastreio = 3;
  var col_n_pedido = 4;
  var col_nome_cliente = 5;
  var col_celular = 6;
  var col_email = 7;
  var col_valor = 8;
  var col_transportadora = 9;
  var col_data_pagamento = 10;
  var col_dias_entrega = 11;


  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var orders = getAllOrders(1).reverse();

  orders.forEach( function( order) {

    sheet.getRange(linha, col_status).setValue(order.status);
    sheet.getRange(linha, col_cd_rastreio).setValue(order.codigo_rastreio);
    sheet.getRange(linha, col_n_pedido).setValue(order.numeroPedido);
    sheet.getRange(linha, col_nome_cliente).setValue(order.nome);
    sheet.getRange(linha, col_celular).setValue(order.telefone);
    sheet.getRange(linha, col_email).setValue(order.email);
    sheet.getRange(linha, col_valor).setValue(order.valor);
    sheet.getRange(linha, col_transportadora).setValue(order.transportadora);
    sheet.getRange(linha, col_data_pagamento).setValue(order.data_pagamento);
    sheet.getRange(linha, col_dias_entrega).setValue(order.prazo);
    linha++;

  });
}