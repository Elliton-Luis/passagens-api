class ViagemInvalidaError(Exception):
    def __init__(self, campo: str, mensagem: str):
        self.campo = campo
        self.mensagem = mensagem
        super().__init__(mensagem)