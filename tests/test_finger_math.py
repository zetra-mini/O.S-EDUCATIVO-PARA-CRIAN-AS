import unittest
import math

def simular_contar_dedos(lm):
    """
    Simulação fiel da função contarDedosRobusto do hud_jarvis.html
    utilizando a geometria matemática rigorosa das 21 juntas.
    """
    if not lm or len(lm) < 21:
        return {"estados": [False, False, False, False, False], "total": 0, "gesto": "nenhum"}

    estados = [False, False, False, False, False]
    palm_size = math.hypot(lm[5][0] - lm[17][0], lm[5][1] - lm[17][1]) or 50

    tips = [8, 12, 16, 20]
    dips = [7, 11, 15, 19]
    pips = [6, 10, 14, 18]
    mcps = [5, 9, 13, 17]

    for i in range(4):
        tip = lm[tips[i]]
        dip = lm[dips[i]]
        pip = lm[pips[i]]
        mcp = lm[mcps[i]]

        d_tip_mcp = math.hypot(tip[0] - mcp[0], tip[1] - mcp[1])
        d_pip_mcp = math.hypot(pip[0] - mcp[0], pip[1] - mcp[1]) or 1
        d_tip_wrist = math.hypot(tip[0] - lm[0][0], tip[1] - lm[0][1])
        d_pip_wrist = math.hypot(pip[0] - lm[0][0], pip[1] - lm[0][1]) or 1

        v1x, v1y = pip[0] - mcp[0], pip[1] - mcp[1]
        v2x, v2y = tip[0] - pip[0], tip[1] - pip[1]
        mag1 = math.hypot(v1x, v1y) or 1
        mag2 = math.hypot(v2x, v2y) or 1
        cos_angle = (v1x * v2x + v1y * v2y) / (mag1 * mag2)

        if tip[1] < pip[1] and tip[1] < dip[1] and (d_tip_mcp > d_pip_mcp * 1.30) and (d_tip_wrist > d_pip_wrist * 1.10) and (cos_angle > 0.35):
            estados[i + 1] = True

    # Trava de pinça
    thumb_tip = lm[4]
    index_tip = lm[8]
    dist_thumb_index_tip = math.hypot(thumb_tip[0] - index_tip[0], thumb_tip[1] - index_tip[1])

    if dist_thumb_index_tip < palm_size * 0.45:
        estados[1] = False
        estados[0] = False
    else:
        outros_dedos_abertos = sum(1 for e in estados[1:] if e)
        thumb_mcp = lm[2]
        thumb_ip = lm[3]
        index_mcp = lm[5]
        middle_mcp = lm[9]

        vt1x, vt1y = thumb_ip[0] - thumb_mcp[0], thumb_ip[1] - thumb_mcp[1]
        vt2x, vt2y = thumb_tip[0] - thumb_ip[0], thumb_tip[1] - thumb_ip[1]
        mag_t1 = math.hypot(vt1x, vt1y) or 1
        mag_t2 = math.hypot(vt2x, vt2y) or 1
        cos_thumb = (vt1x * vt2x + vt1y * vt2y) / (mag_t1 * mag_t2)

        d_tip_mid = math.hypot(thumb_tip[0] - middle_mcp[0], thumb_tip[1] - middle_mcp[1])
        d_tip_idx = math.hypot(thumb_tip[0] - index_mcp[0], thumb_tip[1] - index_mcp[1])
        d_mcp_mid = math.hypot(thumb_mcp[0] - middle_mcp[0], thumb_mcp[1] - middle_mcp[1])
        d_tip_wrist = math.hypot(thumb_tip[0] - lm[0][0], thumb_tip[1] - lm[0][1])
        d_mcp_wrist = math.hypot(thumb_mcp[0] - lm[0][0], thumb_mcp[1] - lm[0][1])

        is_joinha = (
            outros_dedos_abertos == 0 and
            thumb_tip[1] < thumb_ip[1] < thumb_mcp[1] and
            thumb_tip[1] < index_mcp[1] and
            d_tip_wrist > d_mcp_wrist * 1.15 and
            cos_thumb > 0.30
        )

        is_aberto_lateral = (
            d_tip_mid > palm_size * 0.95 and
            d_tip_idx > palm_size * 0.70 and
            d_tip_mid > d_mcp_mid * 1.08 and
            cos_thumb > 0.40
        )

        if is_joinha or is_aberto_lateral:
            estados[0] = True

    total = sum(1 for e in estados if e)
    gesto = "normal"
    if estados[0] and not any(estados[1:]):
        gesto = "joinha"
    elif not estados[0] and estados[1] and estados[2] and not estados[3] and not estados[4]:
        gesto = "paz"

    return {"estados": estados, "total": total, "gesto": gesto}


class TestFingerCountingMath(unittest.TestCase):
    def setUp(self):
        # Base de uma mão padrão: Wrist em (100, 200)
        self.wrist = [100, 200]
        self.index_mcp = [80, 140]
        self.middle_mcp = [100, 135]
        self.ring_mcp = [118, 140]
        self.pinky_mcp = [135, 145]
        self.thumb_mcp = [65, 170]
        self.thumb_ip = [50, 155]

    def _criar_mao(self, dedos_erguidos, polegar_erguido=False):
        lm = [[0, 0] for _ in range(21)]
        lm[0] = list(self.wrist)
        lm[1] = [80, 185]
        lm[2] = list(self.thumb_mcp)
        lm[3] = list(self.thumb_ip)
        
        # Polegar
        if polegar_erguido:
            lm[4] = [25, 140] # Aberto para o lado
        else:
            lm[4] = [90, 150] # Dobrado na palma

        mcps = [self.index_mcp, self.middle_mcp, self.ring_mcp, self.pinky_mcp]
        tips_idx = [8, 12, 16, 20]
        dips_idx = [7, 11, 15, 19]
        pips_idx = [6, 10, 14, 18]
        mcps_idx = [5, 9, 13, 17]

        for i in range(4):
            m = mcps[i]
            lm[mcps_idx[i]] = list(m)
            if i in dedos_erguidos:
                # Estendido
                lm[pips_idx[i]] = [m[0], m[1] - 40]
                lm[dips_idx[i]] = [m[0], m[1] - 70]
                lm[tips_idx[i]] = [m[0], m[1] - 100]
            else:
                # Dobrado para dentro da palma
                lm[pips_idx[i]] = [m[0], m[1] - 25]
                lm[dips_idx[i]] = [m[0], m[1] - 10]
                lm[tips_idx[i]] = [m[0], m[1] + 5]

        return lm

    def test_cinco_dedos(self):
        lm = self._criar_mao([0, 1, 2, 3], polegar_erguido=True)
        res = simular_contar_dedos(lm)
        self.assertEqual(res["total"], 5)
        self.assertTrue(all(res["estados"]))

    def test_quatro_dedos_polegar_na_palma(self):
        # 4 dedos erguidos, polegar recolhido na palma
        lm = self._criar_mao([0, 1, 2, 3], polegar_erguido=False)
        res = simular_contar_dedos(lm)
        self.assertEqual(res["total"], 4)
        self.assertFalse(res["estados"][0]) # Polegar DEVE ser False!
        self.assertTrue(all(res["estados"][1:]))

    def test_tres_dedos_anelar_e_mindinho_fechados(self):
        # 3 dedos (indicador, médio, anelar), polegar e mindinho fechados
        lm = self._criar_mao([0, 1, 2], polegar_erguido=False)
        res = simular_contar_dedos(lm)
        self.assertEqual(res["total"], 3)
        self.assertFalse(res["estados"][0])
        self.assertFalse(res["estados"][4])

    def test_dois_dedos_paz_e_amor(self):
        # 2 dedos (indicador e médio), polegar, anelar e mindinho fechados
        lm = self._criar_mao([0, 1], polegar_erguido=False)
        res = simular_contar_dedos(lm)
        self.assertEqual(res["total"], 2)
        self.assertEqual(res["gesto"], "paz")
        self.assertFalse(res["estados"][0])
        self.assertFalse(res["estados"][3])
        self.assertFalse(res["estados"][4])

    def test_um_dedo_indicador(self):
        # Apenas 1 dedo (indicador)
        lm = self._criar_mao([0], polegar_erguido=False)
        res = simular_contar_dedos(lm)
        self.assertEqual(res["total"], 1)
        self.assertTrue(res["estados"][1])
        self.assertFalse(res["estados"][0])
        self.assertFalse(res["estados"][2])

    def test_zero_dedos_punho_fechado(self):
        lm = self._criar_mao([], polegar_erguido=False)
        res = simular_contar_dedos(lm)
        self.assertEqual(res["total"], 0)
        self.assertFalse(any(res["estados"]))

    def test_joinha_apenas_polegar(self):
        # Apenas polegar erguido para cima
        lm = self._criar_mao([], polegar_erguido=False)
        lm[2] = [65, 170]
        lm[3] = [60, 135]
        lm[4] = [58, 95] # Polegar para cima
        res = simular_contar_dedos(lm)
        self.assertEqual(res["total"], 1)
        self.assertTrue(res["estados"][0])
        self.assertEqual(res["gesto"], "joinha")

if __name__ == '__main__':
    unittest.main()
