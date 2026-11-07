"""Testes da assinatura Ed25519 (rodar: python -m unittest discover -s testes).

Vetores oficiais da RFC 8032, seção 7.1, mais casos de falha e de tempo.
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexsuite import assinatura as ass  # noqa: E402

VETORES = [
    {
        "nome": "TEST 1",
        "sk": "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
        "pk": "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
        "msg": "",
        "sig": (
            "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
            "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
        ),
    },
    {
        "nome": "TEST 2",
        "sk": "4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
        "pk": "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c",
        "msg": "72",
        "sig": (
            "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da"
            "085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00"
        ),
    },
    {
        "nome": "TEST 3",
        "sk": "c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7",
        "pk": "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025",
        "msg": "af82",
        "sig": (
            "6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac"
            "18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a"
        ),
    },
    {
        "nome": "TEST 1024",
        "sk": "f5e5767cf153319517630f226876b86c8160cc583bc013744c6bf255f5cc0ee5",
        "pk": "278117fc144c72340f67d0f2316e8386ceffbf2b2428c9c51fef7c597f1d426e",
        "msg": (
            "08b8b2b733424243760fe426a4b54908632110a66c2f6591eabd3345e3e4eb98"
            "fa6e264bf09efe12ee50f8f54e9f77b1e355f6c50544e23fb1433ddf73be84d8"
            "79de7c0046dc4996d9e773f4bc9efe5738829adb26c81b37c93a1b270b20329d"
            "658675fc6ea534e0810a4432826bf58c941efb65d57a338bbd2e26640f89ffbc"
            "1a858efcb8550ee3a5e1998bd177e93a7363c344fe6b199ee5d02e82d522c4fe"
            "ba15452f80288a821a579116ec6dad2b3b310da903401aa62100ab5d1a36553e"
            "06203b33890cc9b832f79ef80560ccb9a39ce767967ed628c6ad573cb116dbef"
            "efd75499da96bd68a8a97b928a8bbc103b6621fcde2beca1231d206be6cd9ec7"
            "aff6f6c94fcd7204ed3455c68c83f4a41da4af2b74ef5c53f1d8ac70bdcb7ed1"
            "85ce81bd84359d44254d95629e9855a94a7c1958d1f8ada5d0532ed8a5aa3fb2"
            "d17ba70eb6248e594e1a2297acbbb39d502f1a8c6eb6f1ce22b3de1a1f40cc24"
            "554119a831a9aad6079cad88425de6bde1a9187ebb6092cf67bf2b13fd65f270"
            "88d78b7e883c8759d2c4f5c65adb7553878ad575f9fad878e80a0c9ba63bcbcc"
            "2732e69485bbc9c90bfbd62481d9089beccf80cfe2df16a2cf65bd92dd597b07"
            "07e0917af48bbb75fed413d238f5555a7a569d80c3414a8d0859dc65a46128ba"
            "b27af87a71314f318c782b23ebfe808b82b0ce26401d2e22f04d83d1255dc51a"
            "ddd3b75a2b1ae0784504df543af8969be3ea7082ff7fc9888c144da2af58429e"
            "c96031dbcad3dad9af0dcbaaaf268cb8fcffead94f3c7ca495e056a9b47acdb7"
            "51fb73e666c6c655ade8297297d07ad1ba5e43f1bca32301651339e22904cc8c"
            "42f58c30c04aafdb038dda0847dd988dcda6f3bfd15c4b4c4525004aa06eeff8"
            "ca61783aacec57fb3d1f92b0fe2fd1a85f6724517b65e614ad6808d6f6ee34df"
            "f7310fdc82aebfd904b01e1dc54b2927094b2db68d6f903b68401adebf5a7e08"
            "d78ff4ef5d63653a65040cf9bfd4aca7984a74d37145986780fc0b16ac451649"
            "de6188a7dbdf191f64b5fc5e2ab47b57f7f7276cd419c17a3ca8e1b939ae49e4"
            "88acba6b965610b5480109c8b17b80e1b7b750dfc7598d5d5011fd2dcc5600a3"
            "2ef5b52a1ecc820e308aa342721aac0943bf6686b64b2579376504ccc493d97e"
            "6aed3fb0f9cd71a43dd497f01f17c0e2cb3797aa2a2f256656168e6c496afc5f"
            "b93246f6b1116398a346f1a641f3b041e989f7914f90cc2c7fff357876e506b5"
            "0d334ba77c225bc307ba537152f3f1610e4eafe595f6d9d90d11faa933a15ef1"
            "369546868a7f3a45a96768d40fd9d03412c091c6315cf4fde7cb68606937380d"
            "b2eaaa707b4c4185c32eddcdd306705e4dc1ffc872eeee475a64dfac86aba41c"
            "0618983f8741c5ef68d3a101e8a3b8cac60c905c15fc910840b94c00a0b9d0"
        ),
        "sig": (
            "0aab4c900501b3e24d7cdf4663326a3a87df5e4843b2cbdb67cbf6e460fec350"
            "aa5371b1508f9f4528ecea23c436d94b5e8fcd4f681e30a6ac00a9704a188a03"
        ),
    },
]


class VetoresRFC8032(unittest.TestCase):
    def test_vetores(self):
        for v in VETORES:
            with self.subTest(v["nome"]):
                msg = bytes.fromhex(v["msg"])
                self.assertEqual(ass.publica_de(v["sk"]), v["pk"])
                self.assertEqual(ass.assinar(msg, v["sk"]), v["sig"])
                self.assertTrue(ass.verificar(msg, v["sig"], v["pk"]))

    def test_tamanho_mensagem_longa(self):
        self.assertEqual(len(bytes.fromhex(VETORES[3]["msg"])), 1023)


class Assinatura(unittest.TestCase):
    def setUp(self):
        self.priv, self.pub = ass.gerar_chaves()
        self.msg = b"pacote de atualizacao 1.2.3"
        self.sig = ass.assinar(self.msg, self.priv)

    def test_formato_das_chaves(self):
        self.assertEqual(len(self.priv), 64)
        self.assertEqual(len(self.pub), 64)
        self.assertEqual(len(self.sig), 128)
        self.assertEqual(ass.publica_de(self.priv), self.pub)

    def test_ida_e_volta(self):
        self.assertTrue(ass.verificar(self.msg, self.sig, self.pub))

    def test_chaves_diferentes_a_cada_vez(self):
        self.assertNotEqual(ass.gerar_chaves()[0], self.priv)

    def test_mensagem_alterada(self):
        self.assertFalse(ass.verificar(self.msg + b"x", self.sig, self.pub))

    def test_assinatura_alterada(self):
        b = bytearray(bytes.fromhex(self.sig))
        for pos in (0, 31, 32, 63):
            c = bytearray(b)
            c[pos] ^= 0x01
            self.assertFalse(ass.verificar(self.msg, c.hex(), self.pub), pos)

    def test_chave_publica_errada(self):
        _, outra = ass.gerar_chaves()
        self.assertFalse(ass.verificar(self.msg, self.sig, outra))

    def test_s_maior_ou_igual_a_L(self):
        r = bytes.fromhex(self.sig)[:32]
        s = int.from_bytes(bytes.fromhex(self.sig)[32:], "little")
        # S + L representa o mesmo valor módulo L, mas deve ser rejeitado
        s2 = s + ass.L
        self.assertLess(s2, 2**256)
        self.assertFalse(ass.verificar(self.msg, (r + s2.to_bytes(32, "little")).hex(), self.pub))
        self.assertFalse(ass.verificar(self.msg, (r + ass.L.to_bytes(32, "little")).hex(), self.pub))

    def test_entradas_malformadas(self):
        casos = [
            ("zz" * 64, self.pub),
            (self.sig, "zz" * 32),
            (self.sig[:-2], self.pub),
            (self.sig + "00", self.pub),
            (self.sig, self.pub[:-2]),
            (self.sig, self.pub + "00"),
            ("", ""),
            ("abc", self.pub),
            (self.sig, "abc"),
            (None, self.pub),
            (self.sig, None),
        ]
        for sig, pub in casos:
            with self.subTest(sig=sig, pub=pub):
                self.assertIs(ass.verificar(self.msg, sig, pub), False)

    def test_ponto_fora_da_curva(self):
        # y = 2 não tem x correspondente na curva
        fora = (2).to_bytes(32, "little").hex()
        self.assertIs(ass.verificar(self.msg, self.sig, fora), False)
        self.assertIs(ass.verificar(self.msg, fora + self.sig[64:], self.pub), False)
        # y >= p também é inválido
        grande = (ass.P + 1).to_bytes(32, "little").hex()
        self.assertIs(ass.verificar(self.msg, self.sig, grande), False)

    def test_impressao(self):
        imp = ass.impressao(VETORES[0]["pk"])
        grupos = imp.split(" ")
        self.assertEqual([len(g) for g in grupos], [4, 4, 4, 4])
        import hashlib
        esperado = hashlib.sha256(bytes.fromhex(VETORES[0]["pk"])).hexdigest()[:16]
        self.assertEqual("".join(grupos), esperado)

    def test_tempo_da_verificacao(self):
        t0 = time.perf_counter()
        ok = ass.verificar(self.msg, self.sig, self.pub)
        dt = time.perf_counter() - t0
        self.assertTrue(ok)
        self.assertLess(dt, 2.0)


if __name__ == "__main__":
    unittest.main()
