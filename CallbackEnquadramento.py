from Subcamada import Subcamada
from Quadro import Quadro
from enum import Enum
import crc as crc


class Estados(Enum):
    Ocioso = 0
    Recebendo = 1
    Escape = 2

class CallbackEnquadramento(Subcamada):
    '''Classe responsável pelo enquadramento e desenquadramento das mensagens'''


    Flag = b'~'
    Esc = b'}'

    def __init__(self, cnx, tout):
        Subcamada.__init__(self, cnx, tout)
        self.cnx = cnx
        self.disable_timeout()
        self.flag = b'~'
        self.esc = b'}'
        self.e = b'^'
        self.d = b']'
        self.atual = Estados.Ocioso
        self.c = 0
        self.buff = bytearray()

    def handle(self):
        '''Monitora a chegada de dados da Serial'''
        octeto = self.cnx.read(1)
        self.desenquadra(octeto)

    def handle_timeout(self):
        print('Timeout Enquadramento!')
        self.disable_timeout()
        self.desenquadra()

    def enquadra(self, dado):
        '''Realiza o enquadramento'''
        msg = bytearray()
        for c in dado:
            byteC = (c.to_bytes(1, 'little'))
            if byteC == self.flag:
                c = self.esc + self.e
                msg += c
            elif byteC == self.esc:
                c = self.esc + self.d
                msg += c
            else:
                msg.append(c)
        return self.flag + msg + self.flag

    def desenquadra(self, octeto=None):
        '''Analisa os octetos recebidos
            octeto: se for None, é evento timeout'''

        if self.atual == Estados.Ocioso:  # Ocioso
            if octeto is not None:  # octeto recebido
                if octeto == self.flag:
                    self.c = 0
                    self.atual = Estados.Recebendo
                    self.reload_timeout()
                    self.enable_timeout()
                    self.buff.clear()

        elif self.atual == Estados.Recebendo:  # Recebendo
            if octeto is None:  # ocorreu timeout !
                self.atual = Estados.Ocioso
                self.disable_timeout()
            else:
                if octeto == self.esc:
                    self.atual = Estados.Escape
                    self.reload_timeout()
                    self.enable_timeout()
                elif octeto == self.flag:
                    if self.c == 0:
                        pass
                    else:
                        self.atual = Estados.Ocioso
                        self.finaliza(None)
                        self.disable_timeout()
                else:
                    self.c += 1
                    self.buff += octeto

                self.reload_timeout()

        elif self.atual == Estados.Escape:  # Escape
            if octeto is not None:
                if (octeto == self.flag) or (octeto == self.esc):
                    self.atual = Estados.Ocioso
                    self.finaliza(1)
                    self.disable_timeout()
                elif octeto == self.e:
                    self.buff += self.flag
                    self.c += 1
                    self.atual = Estados.Recebendo
                elif octeto == self.d:
                    self.buff += self.esc
                    self.c += 1
                    self.atual = Estados.Recebendo
                else:
                    pass

                self.reload_timeout()

            else:
                self.atual = Estados.Ocioso
                self.disable_timeout()

    def finaliza(self, res=None):
        '''Envia para a camada superior o quadro recebido'''
        if res is None:
            if self.verificaCRC(self.buff):
                quadro = Quadro(self.buff)  # Monta um quadro para a camada superior
                self.upper.recebe(quadro)
        else:
            print('Quadro descartado!')

    def verificaCRC(self, quadro):
        '''Verifica se o quadro está corrompido'''
        fcs = crc.CRC16()
        fcs.clear()
        fcs.update(quadro)
        return fcs.check_crc()

    def gerarCRC(self, quadro):
        '''Gera CRC: insere dois bytes'''
        fcs = crc.CRC16(quadro)
        msg_CRC = fcs.gen_crc()
        fcs.clear()
        return msg_CRC

    def envia(self, quadro):
        '''Realiza a escrita na Serial (recebe dados da camada superior)'''
        msg = quadro.to_bytes()                             # Quadro montando sem FCS
        msg_crc = self.gerarCRC(msg)                        # Quadro completo com FCS
        quadro.fcs_field = msg_crc[-2:]                     # Armazenando FCS
        msg_encoded = self.enquadra(quadro.to_bytes())      # Tratamento de enquadramento
        self.cnx.write(msg_encoded)                         # Enviando mensagem
        quadro.limpa_quadro()                               # Limpa quadro armazenado
