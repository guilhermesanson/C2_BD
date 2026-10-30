from typing import Optional

class Fornecedor:
    """Representa a tabela FORNECEDOR do controle de estoque."""

    def __init__(
        self,
        nome: str,
        cnpj: str,
        logradouro: str,
        numero: str,
        bairro: str,
        cidade: str,
        estado: str,
        cep: str,
        id_fornecedor: Optional[int] = None,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
        complemento: Optional[str] = None,
    ):
        self.__id_fornecedor = id_fornecedor
        self.__nome = nome
        self.__cnpj = cnpj
        self.__telefone = telefone
        self.__email = email
        self.__logradouro = logradouro
        self.__numero = numero
        self.__complemento = complemento
        self.__bairro = bairro
        self.__cidade = cidade
        self.__estado = estado
        self.__cep = cep

    def get_id_fornecedor(self) -> Optional[int]:
        return self.__id_fornecedor

    def set_id_fornecedor(self, id_fornecedor: Optional[int]) -> None:
        self.__id_fornecedor = id_fornecedor

    def get_nome(self) -> str:
        return self.__nome

    def set_nome(self, nome: str) -> None:
        self.__nome = nome

    def get_cnpj(self) -> str:
        return self.__cnpj

    def set_cnpj(self, cnpj: str) -> None:
        self.__cnpj = cnpj

    def get_telefone(self) -> Optional[str]:
        return self.__telefone

    def set_telefone(self, telefone: Optional[str]) -> None:
        self.__telefone = telefone

    def get_email(self) -> Optional[str]:
        return self.__email

    def set_email(self, email: Optional[str]) -> None:
        self.__email = email

    def get_logradouro(self) -> str:
        return self.__logradouro

    def set_logradouro(self, logradouro: str) -> None:
        self.__logradouro = logradouro

    def get_numero(self) -> str:
        return self.__numero

    def set_numero(self, numero: str) -> None:
        self.__numero = numero

    def get_complemento(self) -> Optional[str]:
        return self.__complemento

    def set_complemento(self, complemento: Optional[str]) -> None:
        self.__complemento = complemento

    def get_bairro(self) -> str:
        return self.__bairro

    def set_bairro(self, bairro: str) -> None:
        self.__bairro = bairro

    def get_cidade(self) -> str:
        return self.__cidade

    def set_cidade(self, cidade: str) -> None:
        self.__cidade = cidade

    def get_estado(self) -> str:
        return self.__estado

    def set_estado(self, estado: str) -> None:
        self.__estado = estado

    def get_cep(self) -> str:
        return self.__cep

    def set_cep(self, cep: str) -> None:
        self.__cep = cep

    def to_string(self) -> str:
        return (
            "Fornecedor("
            f"id_fornecedor={self.__id_fornecedor!r}, "
            f"nome={self.__nome!r}, "
            f"cnpj={self.__cnpj!r}, "
            f"telefone={self.__telefone!r}, "
            f"email={self.__email!r}, "
            f"logradouro={self.__logradouro!r}, "
            f"numero={self.__numero!r}, "
            f"complemento={self.__complemento!r}, "
            f"bairro={self.__bairro!r}, "
            f"cidade={self.__cidade!r}, "
            f"estado={self.__estado!r}, "
            f"cep={self.__cep!r}"
            ")"
        )
