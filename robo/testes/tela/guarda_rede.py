"""Registra qualquer tentativa de conexão ou DNS que não seja loopback (e a recusa). Uso: GUARDA_LOG=arq python guarda_rede.py script.py args..."""
import os, sys, socket, runpy, time
LOG = os.environ.get("GUARDA_LOG", "guarda.log")
def reg(m):
    with open(LOG, "a") as f: f.write("%s %s\n" % (time.strftime("%H:%M:%S"), m))
_gai, _conn, _conn_ex = socket.getaddrinfo, socket.socket.connect, socket.socket.connect_ex
def local(h): return str(h) in ("127.0.0.1", "localhost", "::1", "")
def gai(host, *a, **k):
    if not local(host): reg("DNS " + str(host)); raise socket.gaierror("bloqueado pela revisao")
    return _gai(host, *a, **k)
def conn(self, addr):
    h = addr[0] if isinstance(addr, tuple) else addr
    if isinstance(addr, tuple) and not local(h): reg("CONNECT %r" % (addr,)); raise OSError("bloqueado pela revisao")
    return _conn(self, addr)
def conn_ex(self, addr):
    h = addr[0] if isinstance(addr, tuple) else addr
    if isinstance(addr, tuple) and not local(h): reg("CONNECT_EX %r" % (addr,)); return 101
    return _conn_ex(self, addr)
socket.getaddrinfo = gai; socket.socket.connect = conn; socket.socket.connect_ex = conn_ex
reg("guarda ativa: " + " ".join(sys.argv[1:3]))
script = sys.argv[1]; sys.argv = sys.argv[1:]
runpy.run_path(script, run_name="__main__")
