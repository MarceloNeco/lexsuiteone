"""Testes de lexsuite.planilha (escrever_xlsx / ler_xlsx)."""

import datetime as dt
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexsuite.planilha import escrever_xlsx, ler_xlsx  # noqa: E402

try:
    import openpyxl
except ImportError:  # pragma: no cover
    openpyxl = None


class TestPlanilha(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.pasta = self._tmp.name

    def caminho(self, nome="t.xlsx"):
        return os.path.join(self.pasta, nome)

    def abas(self):
        return [
            {"nome": "Dados", "larguras": [12, 30, 8], "linhas": [
                ["Texto", "Número", "Bool"],
                ["A & B <c> \"d\" 'e' ação ✓ 😀", 42, True],
                ["  espaços  ", 3.5, False],
                [None, -7, None],
                [dt.date(2026, 10, 20), dt.datetime(2026, 10, 20, 14, 5), "x\x00y\x0bz"],
            ]},
            {"nome": "Oculta", "oculta": True, "linhas": [["a"], ["b"]]},
            {"nome": "Vazia", "linhas": []},
        ]

    def test_ida_e_volta(self):
        escrever_xlsx(self.caminho(), self.abas())
        r = ler_xlsx(self.caminho())
        self.assertEqual([a["nome"] for a in r["abas"]], ["Dados", "Oculta", "Vazia"])
        self.assertEqual([a["oculta"] for a in r["abas"]], [False, True, False])
        d = r["abas"][0]["linhas"]
        self.assertEqual(d[0], ["Texto", "Número", "Bool"])
        self.assertEqual(d[1], ["A & B <c> \"d\" 'e' ação ✓ 😀", 42, True])
        self.assertIs(d[1][2], True)
        self.assertIsInstance(d[1][1], int)
        self.assertEqual(d[2], ["  espaços  ", 3.5, False])
        self.assertIsInstance(d[2][1], float)
        self.assertEqual(d[3], ["", -7])
        self.assertEqual(d[4], ["2026-10-20", "2026-10-20 14:05", "xyz"])
        self.assertEqual(r["abas"][1]["linhas"], [["a"], ["b"]])
        self.assertEqual(r["abas"][2]["linhas"], [])

    def test_primeira_aba_oculta(self):
        with self.assertRaises(ValueError):
            escrever_xlsx(self.caminho(), [{"nome": "A", "oculta": True, "linhas": []}])

    def test_nome_duplicado_ou_invalido(self):
        with self.assertRaises(ValueError):
            escrever_xlsx(self.caminho(), [{"nome": "A", "linhas": []}, {"nome": "A", "linhas": []}])
        with self.assertRaises(ValueError):
            escrever_xlsx(self.caminho(), [{"nome": "a/b", "linhas": []}])
        with self.assertRaises(ValueError):
            escrever_xlsx(self.caminho(), [{"nome": "x" * 32, "linhas": []}])
        self.assertFalse(os.path.exists(self.caminho()))

    def test_sem_sobras_temporarias(self):
        escrever_xlsx(self.caminho(), self.abas())
        self.assertEqual(os.listdir(self.pasta), ["t.xlsx"])

    def test_limite_descompactado(self):
        p = self.caminho("grande.xlsx")
        with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("xl/workbook.xml", "0" * (51 * 1024 * 1024))
        with self.assertRaises(ValueError):
            ler_xlsx(p)

    @unittest.skipUnless(openpyxl, "openpyxl não disponível")
    def test_openpyxl_le_o_que_escrevemos(self):
        escrever_xlsx(self.caminho(), self.abas())
        wb = openpyxl.load_workbook(self.caminho())
        self.assertEqual(wb.sheetnames, ["Dados", "Oculta", "Vazia"])
        ws = wb["Dados"]
        self.assertEqual(ws["A2"].value, "A & B <c> \"d\" 'e' ação ✓ 😀")
        self.assertEqual(ws["A3"].value, "  espaços  ")
        self.assertEqual(ws["B2"].value, 42)
        self.assertIs(ws["C2"].value, True)
        self.assertEqual(ws["B3"].value, 3.5)
        self.assertTrue(ws["A1"].font.b)
        self.assertFalse(ws["A2"].font.b)
        self.assertEqual(ws.freeze_panes, "A2")
        self.assertEqual(ws.column_dimensions["B"].width, 30)
        self.assertEqual(wb["Oculta"].sheet_state, "hidden")
        self.assertEqual(wb["Dados"].sheet_state, "visible")

    @unittest.skipUnless(openpyxl, "openpyxl não disponível")
    def test_le_arquivo_do_openpyxl(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Primeira"
        ws["A1"] = "nome"
        ws["B1"] = "valor"
        ws["A2"] = "João"
        ws["B2"] = 10
        ws["D2"] = 2.5       # C2 pulada
        ws["A3"] = "=B2*2"
        ws["B3"] = True
        ws2 = wb.create_sheet("Escondida")
        ws2["B1"] = "só na B"
        ws2.sheet_state = "hidden"
        p = self.caminho("op.xlsx")
        wb.save(p)
        r = ler_xlsx(p)
        self.assertEqual([a["nome"] for a in r["abas"]], ["Primeira", "Escondida"])
        self.assertEqual([a["oculta"] for a in r["abas"]], [False, True])
        l = r["abas"][0]["linhas"]
        self.assertEqual(l[0], ["nome", "valor"])
        self.assertEqual(l[1], ["João", 10, "", 2.5])
        self.assertEqual(l[2][1], True)
        self.assertEqual(r["abas"][1]["linhas"], [["", "só na B"]])

    @unittest.skipUnless(openpyxl, "openpyxl não disponível")
    def test_formula_com_valor_em_cache_e_shared_strings(self):
        # Monta à mão um pacote com sharedStrings e fórmula com <v> em cache,
        # e com a aba 1 apontando para sheet2.xml (ordem não é sheetN).
        p = self.caminho("man.xlsx")
        ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
        rn = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
        with zipfile.ZipFile(p, "w") as z:
            z.writestr("xl/workbook.xml",
                       f'<workbook {ns} {rn}><sheets><sheet name="Z" sheetId="1" r:id="rId9"/>'
                       '<sheet name="H" sheetId="2" state="veryHidden" r:id="rId8"/></sheets></workbook>')
            z.writestr("xl/_rels/workbook.xml.rels",
                       '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       '<Relationship Id="rId9" Type="x" Target="worksheets/sheet2.xml"/>'
                       '<Relationship Id="rId8" Type="x" Target="/xl/worksheets/sheet1.xml"/></Relationships>')
            z.writestr("xl/sharedStrings.xml",
                       f'<sst {ns}><si><t>um</t></si><si><r><t>do</t></r><r><t>is</t></r></si></sst>')
            z.writestr("xl/worksheets/sheet2.xml",
                       f'<worksheet {ns}><sheetData><row r="2"><c r="B2" t="s"><v>1</v></c>'
                       '<c r="C2"><f>1+1</f><v>2</v></c><c t="str"><f>"a"</f><v>a</v></c></row>'
                       '<row r="5"><c r="A5" t="s"><v>0</v></c><c r="B5"/></row></sheetData></worksheet>')
            z.writestr("xl/worksheets/sheet1.xml", f'<worksheet {ns}><sheetData/></worksheet>')
        r = ler_xlsx(p)
        self.assertEqual(r["abas"][0]["nome"], "Z")
        self.assertEqual(r["abas"][0]["linhas"], [["", "dois", 2, "a"], ["um"]])
        self.assertTrue(r["abas"][1]["oculta"])


if __name__ == "__main__":
    unittest.main()
