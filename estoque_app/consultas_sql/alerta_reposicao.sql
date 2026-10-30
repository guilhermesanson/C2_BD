SELECT p.id_produto,
       p.nome AS produto,
       p.quantidade,
       f.nome AS fornecedor,
       f.telefone
FROM PRODUTO p
JOIN FORNECEDOR f ON f.id_fornecedor = p.id_fornecedor
