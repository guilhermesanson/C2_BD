SELECT p.id_produto,
       p.nome AS produto,
       p.preco,
       p.quantidade,
       f.id_fornecedor,
       f.nome AS fornecedor,
       f.cnpj
FROM PRODUTO p
JOIN FORNECEDOR f ON f.id_fornecedor = p.id_fornecedor
ORDER BY p.nome, p.id_produto
