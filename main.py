from serial import Serial
import poller
import sys
from CallbackEnquadramento import CallbackEnquadramento
from CallbackARQ import CallbackARQ
from CallbackTun import CallbackTun
from tun import Tun
from argparse import ArgumentParser

if __name__ == "__main__":

    Timeout = 10 # Segundos

    parser = ArgumentParser()
    parser.add_argument('--serial',
                        "-s",
                        help="Porta serial",
                        required=True)
    parser.add_argument('--iporigem',
                        "-ipo",
                        help="Ip de origem",
                        required=True)
    parser.add_argument('--ipdestino',
                        "-ipd",
                        help="Ip de destino",
                        required=True)

    args = parser.parse_args()

    porta = '{}'.format(args.serial)
    ipOrigem = '{}'.format(args.iporigem)
    ipDestino = '{}'.format(args.ipdestino)

    try:
        cnx = Serial(porta, timeout=0)
        print('Porta utilizada: %s' % porta)
    except Exception as e:
        print('Erro')
        sys.exit(0)

    # CallbackTun
    tun = Tun("tun0", ipOrigem, ipDestino, mtu=1024)
    tun.start()
    cbTun = CallbackTun(tun)

    # Callback ARQ
    arq = CallbackARQ(Timeout)

    # Callback Enquadramento
    enquadra = CallbackEnquadramento(cnx, Timeout)

    # Conecta os Callbacks
    arq.conecta(cbTun)
    enquadra.conecta(arq)

    # Despache Poller
    sched = poller.Poller()
    sched.adiciona(enquadra)
    sched.adiciona(cbTun)
    sched.adiciona(arq)
    sched.despache()