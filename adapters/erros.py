class ViagemInvalidaError(Exception):
    def __init__(self, campo: str, mensagem: str):
        self.campo = campo
        self.mensagem = mensagem
        super().__init__(mensagem)


class FormatoNaoReconhecidoError(Exception):
    def __init__(self, mensagem: str = "O formato do payload não corresponde a nenhuma companhia suportada."):
        self.mensagem = mensagem
        super().__init__(mensagem)
