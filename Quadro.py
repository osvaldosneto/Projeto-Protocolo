class Quadro:

    def __init__(self, quadro=None):
        if quadro is None:
            self._ctrl = 0
            self._res = 0
            self._id = 0
            self.data = b''
            self._fcs = b''
            self._headerlen = 3
            self._payloadlen = 1024
            self._fcslen = 2
        else:  # Quadro recebido ('desmontando')
            self._ctrl = quadro[0]
            self._res = quadro[1]
            self._id = quadro[2]
            self.data = quadro[3:-2]
            self._fcs = quadro[-2:]

    @property
    def sequencia(self):
        ''' Getter para o valor de nSeq '''
        seq = self._ctrl & 8  # 0b1000
        return seq >> 3

    @sequencia.setter
    def sequencia(self, nseq):
        ''' Setter para o valor de nSeq '''
        # if not nSeq in (1, 0) : raise ValueError('Número de sequência deve ser 0 ou 1')
        self._ctrl = self._ctrl & 0xf7  # 0b11110111 ('zerando' o valor do bit 3)
        self._ctrl |= (nseq << 3)

    @property
    def tipo(self):
        ''' Getter para o tipo do quadro '''
        seq = self._ctrl & 0x80 # 0b10000000
        return seq >> 7

    @tipo.setter
    def tipo(self, tipo):
        ''' Setter para o tipo do quadro '''
        # if not tipo in (1, 0): raise ValueError('tipo deve ser Quadro.ACK ou Quadro.DATA')
        self._ctrl = self._ctrl & 0x7f  # 0b01111111
        self._ctrl |= (tipo << 7)

    @property
    def controle(self):
        ''' Getter para o campo controle inteiro '''
        return self._ctrl

    @property
    def reservado(self):
        ''' Getter para o campo reservado '''
        return self._res

    @reservado.setter
    def reservado(self, res):
        ''' Setter para o campo reservado '''
        self._res = res

    @property
    def id_proto(self):
        ''' Getter para o campo id_proto '''
        return self._id

    @id_proto.setter
    def id_proto(self, id):
        ''' Setter para o campo id_proto '''
        self._id = id

    @property
    def fcs_field(self):
        ''' Getter para o campo fcs '''
        return self._fcs

    @fcs_field.setter
    def fcs_field(self, fcs):
        ''' Setter para o campo fcs '''
        self._fcs = fcs

    @property
    def payload(self):
        ''' Getter para o campo payload '''
        return self.data

    @payload.setter
    def payload(self, data):
        ''' Setter para o campo payload '''
        self.data = data

    def to_bytes(self):
        ''' Retorna o quadro inteiro no formato de bytes '''
        buf = bytearray()
        buf.append(self._ctrl)
        buf.append(self._res)
        buf.append(self._id)
        buf += self.data
        buf += self._fcs
        return bytes(buf)

    def limpa_quadro(self):
        self._ctrl = 0
        self._res = 0
        self._id = 0
        self.data = b''
        self._fcs = b''
