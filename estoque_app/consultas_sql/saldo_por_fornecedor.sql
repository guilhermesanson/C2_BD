SELECT f.id_fornecedor,
       f.nome AS fornecedor,
       COUNT(p.id_produto) AS produtos_cadastrados,
       NVL(SUM(p.quantidade), 0) AS unidades_em_estoque,
       NVL(SUM(p.preco * p.quantidade), 0) AS valor_do_estoque
FROM FORNECEDOR f
LEFT JOIN PRODUTO p ON p.id_fornecedor = f.id_fornecedor
GROUP BY f.id_fornecedor, f.nome
ORDER BY f.nome, f.id_fornecedor
