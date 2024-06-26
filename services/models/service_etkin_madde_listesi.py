# -*- coding: utf8 -*-

#
#
# -*- Etkin Madde Listesi Sorgula Servisi -*-
#
#
import datetime

from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class EtkinMaddeListesiSorgula(models.Model):
    _name = "service.etkin_madde_listesi"
    _description = "Etkin Madde Listesi Servisi"

    tesis_kod = fields.Char(string="Tesis Kodu")
    doctor_id = fields.Many2one('hospital.doctor', string="Doktor")

    etkin_madde_ids = fields.Many2many('hospital.etkin_maddedvo', string="Etkin Madde Listesi")

    def etkin_madde_listesi_sorgula(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiYardimciIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken('99999999990', '99999999990'))

        vals = {
            'arg0': {
                'tesisKodu': int(self.tesis_kod),
                'doktorTcKimlikNo': int(self.doctor_id.doctor_tc)
            }
        }
        with client.settings(strict=False):
            etkin_madde_listesi = client.service.etkinMaddeListesiSorgula(**vals)
        result = etkin_madde_listesi.etkinMaddeListesi

        if etkin_madde_listesi.sonucKodu == '0000':
            my_etkin_madde_kod = self.env['hospital.etkin_maddedvo'].search([]).mapped('etkin_madde_kodu')
            not_in_my_etkin_madde = filter(lambda r: r.kodu not in my_etkin_madde_kod, result)
            for etkin_madde in not_in_my_etkin_madde:
                self.env['hospital.etkin_maddedvo'].create({
                    'etkin_madde_kodu': etkin_madde.kodu,
                    'etkin_madde_adi': etkin_madde.adi,
                    'etkin_madde_formu': etkin_madde.formu
                })
                my_etkin_madde = self.env['hospital.etkin_maddedvo'].search([('etkin_madde_kodu', '=', etkin_madde.kodu)])

                self.etkin_madde_ids = [(4, my_etkin_madde.id, 0)]

            return {
                'name': 'Yeni Eklenen Etkin Maddeler',
                'type': 'ir.actions.act_window',
                'res_model': 'hospital.etkin_maddedvo.wizard',
                'target': 'new',
                'view_type': 'form',
                'view_mode': 'form',
                'context': {
                    'default_etkin_madde_ids': [(4, e_madde.id) for e_madde in self.etkin_madde_ids]
                }
            }
        else:
            return {
                'name': 'Sonuç Mesajı',
                'type': 'ir.actions.act_window',
                'res_model': 'sonuc.mesaji.wizard',
                'target': 'new',
                'view_mode': 'form',
                'context': {
                    'default_sonuc_kodu': etkin_madde_listesi.sonucKodu,
                    'default_sonuc_mesaji': etkin_madde_listesi.sonucMesaji,
                }
            }
