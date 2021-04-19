from poller import Callback


class Subcamada(Callback):

    def __init__(self, fd, tout):
        Callback.__init__(self, fd, tout)
        self.upper = None
        self.lower = None

    def envia(self, quadro):
        '''Método abstrato'''
        raise NotImplementedError('abstrato')

    def recebe(self, quadro):
        '''Método abstrato'''
        raise NotImplementedError('abstrato')

    def conecta(self, superior):
        '''Conexão entre camadas'''
        self.upper = superior
        superior.lower = self
