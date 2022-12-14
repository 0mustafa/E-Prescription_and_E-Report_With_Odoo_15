# -*- coding: utf8 -*-

#
#
# -*- Ilaç Açıklama Ekleme Servisi -*-
#
#


from odoo import models, fields
from zeep import Client
from zeep.wsse.username import UsernameToken


class MedicineExplanation(models.Model):
    _name = "hospital.medicine.explanation"
    _description = "Medicine Explanation"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # for Chatter

    tesis_kodu = fields.Char(string="Tesis Kodu")
    doctor_id = fields.Many2one('hospital.doctor', string="Doktor")
    erecete_no = fields.Char(string="E-Reçete No")
    medicine_id = fields.Many2one('hospital.medicine', string="İlaç")
    aciklama_turu = fields.Selection([
        ('1', 'Teşhis/Tanı'),
        ('2', 'Tedavi Süresi'),
        ('3', 'Hasta Güvenlik ve İzleme Formu'),
        ('4', 'Tetkik Sonucu'),
        ('5', 'Endikasyon Dışı Kullanım İzni'),
        ('99', 'Diğer')
    ], string="E-Reçete Açıklama Türü")
    aciklama = fields.Char(string="E-Reçete Açıklaması")

    def action_submit(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiReceteIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken('99999999990', '99999999990'))

        for rec in self:
            vals = {
                'arg0': {
                    'ereceteNo': rec.erecete_no,
                    'barkod': int(rec.medicine_id.barcode),
                    'tesisKodu': int(rec.tesis_kodu),
                    'doktorTcKimlikNo': int(rec.doctor_id.doctor_tc),
                    'ereceteIlacAciklamaDVO': {
                        'aciklama': rec.aciklama,
                        'aciklamaTuru': int(rec.aciklama_turu)
                    }
                }
            }

        return {
            'name': 'Sonuç Mesajı',
            'type': 'ir.actions.act_window',
            'res_model': 'sonuc.mesaji.wizard',
            'target': 'new',
            'view_mode': 'form',
            'context': {
                'default_sonuc_kodu': client.service.ereceteIlacAciklamaEkle(**vals).sonucKodu,
                'default_sonuc_mesaji': client.service.ereceteIlacAciklamaEkle(**vals).sonucMesaji,
            }
        }
