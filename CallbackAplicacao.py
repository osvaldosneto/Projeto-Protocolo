import sys
from Subcamada import Subcamada
from Quadro import Quadro


class CallbackAplicacao(Subcamada):
    '''Classe responsável pela leitura do teclado'''

    def __init__(self, file):
        self.msg_length = 128
        self.quadro = Quadro()
        if file != None:
            Subcamada.__init__(self, file, 0)
            self.file = True
        else:
            Subcamada.__init__(self, sys.stdin, 0)
            self.file = False

    def handle(self):
        ''' Leitura do teclado e chama enquadra() da classe CallbackEnquadramento '''
        if self.file:
            l = self.fd.read(self.msg_length)
            if l != b'':
                self.quadro.payload = l            # payload do quadro
                self.lower.envia(self.quadro)      # passando o quadro para a subcamada
            else:
                self.disable()
        else:
            l = bytes(sys.stdin.readline().encode('UTF-8'))[:-1]
            self.quadro.payload = l                # payload do quadro
            self.lower.envia(self.quadro)          # passando o quadro para a subcamada

    def recebe(self, quadro):
        print("RX:", quadro.data.decode('UTF-8'))
