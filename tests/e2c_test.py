#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from nose.plugins.attrib import attr
import mail2calendar


class Events2CalendarTests(unittest.TestCase):
    @attr('interactive')
    def test_something(self):
        self.assertEqual(True, False)

    def test_format_event(self):
        e2c = mail2calendar.Events2Calendar()
        e2c.parse_text("\
Naháňka\
29.10. 8:30 Smrková hora-Brtí LCH Harm.Kozí Sz: za Žďárem\
12.11. 8:30 Bož.Hora + Bažanti LCH Čada Sz: Volší za Božtěšicemi\
26.11. 8:30 Němčice – Mladotice LCH Denk Václav Sz: Pěry – horní roh\
10.12. 8:30 Lukavice – Chvojová Hora „U Jelena“ POSLEDNÍ LEČ (ženy) Sz: Kazatelna Jiřík ml. Kolovanka- Trefanec\
26.12. So. 8:30 Blata – Záhorčice LCH Čada Sz: kazatelna Průchovo- obrázek\
30.12. Pá. 8:30 MS Strážov + MS Běšiny Běšiny (Kemp) Sz:Javoří u Hrabičkáře\
7.1. So. 8:30 Splž LCH Harm.Kozí Sz: skládka 'nad Pechrem'".decode("utf8")
                       )
        formated_event = e2c._format_event(e2c.mevents[0])
        print formated_event
        self.assertTrue(False)





if __name__ == '__main__':
    unittest.main()
