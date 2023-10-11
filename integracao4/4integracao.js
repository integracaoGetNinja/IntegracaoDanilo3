function atualizar() {
  var planilha = SpreadsheetApp.openById('1JSFOMrwVpExTAmKk-3PpQgSQDaid-E8EHJOjlTEC0d0');

    // Acessa o Sheet1 pelo nome
  var clientes = planilha.getSheetByName('Clientes');

  // Acessa o Sheet2 pelo nome
  var folha2 = planilha.getSheetByName('Folha2');

  var dataInicial = converterData(clientes.getRange(4, 2).getValue());
  var dataFinal = converterData(clientes.getRange(4, 3).getValue());

  var linha = 9;

  var col_nome = 2;
  var col_email = 3;
  var col_celular = 4;
  var col_quantidadeCompra = 5;
  var col_valores = 6;

  getDatas(dataInicial, dataFinal).forEach( function( order ){

      clientes.getRange(linha, col_nome).setValue( order.nomeCliente );
      clientes.getRange(linha, col_email).setValue( order.email );
      clientes.getRange(linha, col_celular).setValue( order.telefone );
      clientes.getRange(linha, col_quantidadeCompra).setValue( order.quatidadeCompras );
      clientes.getRange(linha, col_valores).setValue( "R$ "+order.valores );

      linha++;
  });

  var linha = 9;
  var col_produto = 2;
  var col_quantidade = 3;
  var col_valor = 4;

  get_data_product(dataInicial, dataFinal).forEach( function (product) {

    folha2.getRange(linha, col_produto).setValue(product.nomeProduto);
    folha2.getRange(linha, col_quantidade).setValue(product.quantidade);
    folha2.getRange(linha, col_valor).setValue("R$ "+product.valor);
    linha++;
  });

}

function converterData(dataString) {
  // Cria um objeto Date com a string de data fornecida
  var data = new Date(dataString);

  // Obtém o ano, mês e dia do objeto Date
  var ano = data.getFullYear();
  // Adiciona 1 ao mês, pois os meses em JavaScript vão de 0 a 11
  var mes = (data.getMonth() + 1).toString().padStart(2, '0');
  var dia = data.getDate().toString().padStart(2, '0');

  // Cria a string no formato "ano-mes-dia"
  var dataFormatada = ano + '-' + mes + '-' + dia;

  return dataFormatada;
}

function getDatas(dataInicial, dataFinal) {
  var url = "https://api.awsli.com.br/v1/pedido/search/?since_criado=" + dataInicial + "&until_criado=" + dataFinal;

  var headers = {
    "Authorization": "chave_api 32b19b99033db32ab955 aplicacao 120f779a-59dc-4351-92f6-857efd50362a"
  };

  var response = UrlFetchApp.fetch(url, {
    "headers": headers
  });

  var ordersUtils = JSON.parse(response.getContentText()).objects;
  var nextOrders = JSON.parse(response.getContentText()).meta.next;

  while (nextOrders) {
    url = "https://api.awsli.com.br" + nextOrders;

    responseMoreOrders = UrlFetchApp.fetch(url, {
      "headers": headers
    });

    var responseMoreOrdersJson = JSON.parse(responseMoreOrders.getContentText());

    ordersUtils = ordersUtils.concat(responseMoreOrdersJson.objects);
    nextOrders = responseMoreOrdersJson.meta.next;
  }

  var orderClean = [];

  var srcs = [];
  for (var i = 0; i < ordersUtils.length; i++) {
    var order = ordersUtils[i];
    if (order.situacao.aprovado) {
      srcs.push(order.resource_uri);
    }
  }

  for (var j = 0; j < srcs.length; j++) {
    url = "https://api.awsli.com.br" + srcs[j];

    responseSrc = UrlFetchApp.fetch(url, {
      "headers": headers
    });

    var responseSrcJson = JSON.parse(responseSrc.getContentText());
    var itens = responseSrcJson.itens;

    if (itens.length > 1) {
      for (var k = 0; k < itens.length; k++) {
        orderClean.push({
          "telefone": responseSrcJson.cliente.telefone_celular,
          "nomeCliente": responseSrcJson.cliente.nome,
          "email": responseSrcJson.cliente.email,
          "quatidadeCompras": itens[k].quantidade,
          "valores": responseSrcJson.pagamentos[0].valor_pago
        });
      }
    } else {
      orderClean.push({
        "telefone": responseSrcJson.cliente.telefone_celular,
        "nomeCliente": responseSrcJson.cliente.nome,
        "email": responseSrcJson.cliente.email,
        "quatidadeCompras": itens[0].quantidade,
        "valores": responseSrcJson.pagamentos[0].valor_pago
      });
    }
  }

  return orderClean;
}

function get_data_product(dataInicial, dataFinal) {
  var url = "https://api.awsli.com.br/v1/pedido/search/?since_criado=" + dataInicial + "&until_criado=" + dataFinal;
  var headers = {
    'Authorization': 'chave_api 32b19b99033db32ab955 aplicacao 120f779a-59dc-4351-92f6-857efd50362a'
  };

  var response = UrlFetchApp.fetch(url, {
    headers: headers,
    method: 'GET'
  });

  var responseData = JSON.parse(response.getContentText());
  var ordersUtils = responseData.objects;
  var nextOrders = responseData.meta.next;

  while (nextOrders) {
    var responseMoreOrders = UrlFetchApp.fetch("https://api.awsli.com.br" + nextOrders, {
      headers: headers,
      method: 'GET'
    });
    var moreOrdersData = JSON.parse(responseMoreOrders.getContentText());
    ordersUtils = ordersUtils.concat(moreOrdersData.objects);
    nextOrders = moreOrdersData.meta.next;
  }

  var listProducts = [];

  var srcs = [];
  for (var i = 0; i < ordersUtils.length; i++) {
    var order = ordersUtils[i];
    if (order.situacao.aprovado) {
      srcs.push(order.resource_uri);
    }
  }

  for (var j = 0; j < srcs.length; j++) {
    var src = srcs[j];
    var responseSrc = UrlFetchApp.fetch("https://api.awsli.com.br" + src, {
      headers: headers,
      method: 'GET'
    });
    var srcData = JSON.parse(responseSrc.getContentText());
    var itens = srcData.itens;

    if (itens.length > 1) {
      for (var k = 0; k < itens.length; k++) {
        var item = itens[k];
        var product = {
          "nomeProduto": item.nome,
          "quantidade": parseInt(item.quantidade.replace('.', '')),
          "valor": item.preco_venda
        };
        listProducts = verifyAddedInList(listProducts, product);
      }
    } else {
      var product = {
        "nomeProduto": itens[0].nome,
        "quantidade": parseInt(itens[0].quantidade.replace('.', '')),
        "valor": itens[0].preco_venda
      };
      listProducts = verifyAddedInList(listProducts, product);
    }
  }
  return listProducts;
}

function verifyAddedInList(listProducts, product) {
  var inList = false;
  for (var i = 0; i < listProducts.length; i++) {
    if (listProducts[i].nomeProduto === product.nomeProduto) {
      listProducts[i].quantidade += product.quantidade;
      inList = true;
      break;
    }
  }

  if (!inList) {
    listProducts.push(product);
  }

  return listProducts;
}


