from decimal import Decimal
from typing import Optional

from .empresa_fornecedora import Fornecedor

class Produto:
    """Representa PRODUTO; fornecedor armazena a associação com um objeto Fornecedor."""

    def __init__(
        self,
        nome: str,
        preco: Decimal,
        quantidade: int,
        fornecedor: Fornecedor,
        id_produto: Optional[int] = None,
        descricao: Optional[str] = None,
    ):
        self.__id_produto = id_produto
        self.__nome = nome
        self.__descricao = descricao
        self.__preco = preco
        self.__quantidade = quantidade
        self.__fornecedor = fornecedor

    def get_id_produto(self) -> Optional[int]:
        return self.__id_produto

    def set_id_produto(self, id_produto: Optional[int]) -> None:
        self.__id_produto = id_produto

    def get_nome(self) -> str:
        return self.__nome

    def set_nome(self, nome: str) -> None:
        self.__nome = nome

    def get_descricao(self) -> Optional[str]:
        return self.__descricao

    def set_descricao(self, descricao: Optional[str]) -> None:
        self.__descricao = descricao

    def get_preco(self) -> Decimal:
        return self.__preco

    def set_preco(self, preco: Decimal) -> None:
        self.__preco = preco

    def get_quantidade(self) -> int:
        return self.__quantidade

    def set_quantidade(self, quantidade: int) -> None:
        self.__quantidade = quantidade

    def get_fornecedor(self) -> Fornecedor:
        return self.__fornecedor

    def set_fornecedor(self, fornecedor: Fornecedor) -> None:
        self.__fornecedor = fornecedor

    def to_string(self) -> str:
        return (
            "Produto("
            f"id_produto={self.__id_produto!r}, "
            f"nome={self.__nome!r}, "
            f"descricao={self.__descricao!r}, "
            f"preco={self.__preco!r}, "
            f"quantidade={self.__quantidade!r}, "
            f"fornecedor={self.__fornecedor.to_string()}"
            ")"
        )
