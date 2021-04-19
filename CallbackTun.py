from Subcamada import Subcamada
from Quadro import Quadro

class CallbackTun(Subcamada):
    '''Classe responsável pela integração com o Linux'''

    def __init__(self, tun):
        Subcamada.__init__(self, tun.fd, 0)
        self._tun = tun
        self.protoIpv4 = 2048
        self.protoIpv6 = 34525

    def handle(self):
        quadro = Quadro()
        proto, frame = self._tun.get_frame()        #capturando frame da serial

        if proto == self.protoIpv4:                 #setando id proto para ipv4
            quadro.id_proto = 1

        elif proto == self.protoIpv6:               #setando id proto para ipv6
            quadro.id_proto = 2

        else:
            print('Problemas ao setar IdProto')

        quadro.data = frame
        self.lower.envia(quadro)                    #enviando quadro para a camada inferior (ARQ)

    def recebe(self, quadro):

        if quadro.id_proto == 1:
            self._tun.send_frame(quadro.data, self.protoIpv4)   #enviando quadro recebido para o sistema

        elif quadro.id_proto == 2:
            self._tun.send_frame(quadro.data, self.protoIpv6)   #enviando quadro recebido para o sistema

        else:
            print('Problemas ao receber quadro')
