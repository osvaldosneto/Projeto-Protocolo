import sys
from Subcamada import Subcamada
from Quadro import Quadro
from enum import Enum
import random


class Estados(Enum):
    Ocioso = 0
    Espera = 1
    BackoffTX = 2
    BackoffRX = 3


class TipoEvento(Enum):
    DATA = 0
    Payload = 1
    Timeout = 2
    ACK_TX = 3
    Timer_OK = 4


class Evento:

    def __init__(self, tipo, dados):
        self.tipo = tipo
        self.dados = dados


class CallbackARQ(Subcamada):
    '''Classe responsável pela garantia de entrega'''

    def __init__(self, tout):
        Subcamada.__init__(self, None, tout)
        self.disable_timeout()
        self.rx = 0
        self.tx = 0
        self.atual = Estados.Ocioso
        self.quadroACK = Quadro()
        self.quadroANTERIOR = Quadro()
        self.timeslot = 0.1

    def handle_timeout(self):
        e = Evento(TipoEvento.Timeout, None)
        self.mecanismoARQ(e)

    def mecanismoARQ(self, evento):
        ''' MEF mecanismo ARQ: Parâmetro deve ser um objeto Evento '''

        if self.atual == Estados.Ocioso:  # Ocioso
            if evento.tipo == TipoEvento.DATA:
                self.tratamentoEventoData(evento.dados)

            elif evento.tipo == TipoEvento.Payload:
                # print('payload', self.atual)
                self.atual = Estados.Espera
                evento.dados.sequencia = self.tx
                evento.dados.tipo = 0
                self.quadroANTERIOR = evento.dados           # Armazena quadro enviado
                self.lower.envia(evento.dados)
                self.reload_timeout()
                self.enable_timeout()                        # Habilitando Timeout padrao
                self.upper.disable()                         # Bloqueia recebimento de dados superiores
            else:
                print('erro ARQ')

        elif self.atual == Estados.Espera:  # Espera
            if evento.tipo == TipoEvento.DATA:
                self.tratamentoEventoData(evento.dados)

            elif evento.tipo == TipoEvento.Timeout:
                # print('timeout',self.atual)
                self.atual = Estados.BackoffTX                          # Mudando de estado
                self.enable_timeout()                                   # Habilitando timer

            elif evento.tipo == TipoEvento.ACK_TX:
                if evento.dados.sequencia != self.tx:
                    # print('ACK tx errado', self.atual)
                    self.atual = Estados.BackoffTX                      # Mudando de estado
                    timer = self.timeslot * random.randint(0, 7)
                    self.timeout = timer                                # Habilitando timer
                    # self.reload_timeout()
                    self.enable_timeout()
                else:
                    # print('ACK tx certo', self.atual)
                    self.tx = self.tx ^ 1
                    self.atual = Estados.BackoffRX
                    timer = self.timeslot * random.randint(0, 7)
                    self.timeout = timer                                # Habilitando timer
                    # self.reload_timeout()
                    self.enable_timeout()
            else:
                print('erro ARQ')

        elif self.atual == Estados.BackoffTX:  # BackoffTX
            if evento.tipo == TipoEvento.DATA:
                self.tratamentoEventoData(evento.dados)

            elif evento.tipo == TipoEvento.Timeout:
                # print('reenviando')
                self.lower.envia(self.quadroANTERIOR)         # Retransmissão quadro ack_not_TX
                self.atual = Estados.Espera                   # Mudanca de estado
                self.reload_timeout()
                self.enable_timeout()                         # Timeout padrao

        elif self.atual == Estados.BackoffRX:  # BackoffRX
            if evento.tipo == TipoEvento.DATA:
                self.tratamentoEventoData(evento.dados)
                self.disable_timeout()
                self.atual = Estados.Ocioso
                self.upper.enable()

            elif evento.tipo == TipoEvento.Timeout:
                # print('voltando para ocioso')
                self.atual = Estados.Ocioso                   # Mudanca de estado
                self.upper.enable()                           # Habilitando camada superior
                self.disable_timeout()

        else:
            print('Estado MEF não existente!')

    def tratamentoEventoData(self, quadro):
        ''' Realiza o tratamento de um evento do tipo DATA '''
        if quadro.sequencia == self.rx:
            # print('enviando confirmação correta', self.atual)
            self.upper.recebe(quadro)                   # Enviando quadro para Aplicacao
            self.quadroACK.sequencia = self.rx          # Bit sequencia campo controle quadro ACK
            self.quadroACK.tipo = 1                     # Bit tipo campo controle quadro ACK
            self.lower.envia(self.quadroACK)            # Enviando confirmacação para Enquadramento
            self.rx = self.rx ^ 1
        elif quadro.sequencia != self.rx:
            # print('enviando confirmação errada', self.atual)
            self.quadroACK.sequencia = quadro.sequencia
            self.quadroACK.tipo = 1
            self.lower.envia(self.quadroACK)

    def envia(self, quadro):
        ''' Recebe dados de cima e envia para baixo '''
        e = Evento(TipoEvento.Payload, quadro)               # Dados vindos da aplicação
        self.mecanismoARQ(e)

    def recebe(self, quadro):
        ''' Recebe dados de baixo e envia para cima '''
        if quadro.tipo == 0:
            e = Evento(TipoEvento.DATA, quadro)
        else:
            e = Evento(TipoEvento.ACK_TX, quadro)

        self.mecanismoARQ(e)




