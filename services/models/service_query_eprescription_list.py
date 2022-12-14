# -*- coding: utf8 -*-

#
#
# -*- E-Reçete Liste Sorgula Servisi -*-
#
#
import datetime

from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class QueryEprescriptionList(models.Model):
    _name = "service.query.eprescription.list"
    _description = "Hospital Query Eprescription List Service"

    tesis_kod = fields.Char(string="Tesis Kodu")
    doctor_id = fields.Many2one('hospital.doctor', string="Doktor")
    patient_id = fields.Many2one('hospital.epatient', string="Hasta")
    eprescriptions_list = fields.Many2many('hospital.eprescription', string="Hastaya ait e-reçeteler")

    def query_eprescription_list(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiReceteIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken('99999999990', '99999999990'))

        vals = {
            'arg0': {
                'tesisKodu': int(self.tesis_kod),
                'doktorTcKimlikNo': int(self.doctor_id.doctor_tc),
                'hastaTcKimlikNo': int(self.patient_id.tc_no)
            }
        }

        with client.settings(strict=False):
            erecete = client.service.ereceteListeSorgu(**vals)
        result = erecete.ereceteListesi

        if erecete.sonucKodu == '0000':

            eprescription_list = []
            for recete in result:

                eprescription = self.env['hospital.eprescription'].search([('erecete_no', '=', recete.ereceteNo)])
                if eprescription:
                    self.eprescriptions_list = [(4, eprescription.id)]
                """
                eprescriptions_list.append({
                    'seri_no': recete.ereceteNo,
                    'doctor_name': recete.doktorAdi,
                    'doctor_surname': recete.doktorSoyadi,
                    'today': datetime.datetime.strptime(recete.receteTarihi, "%d.%m.%Y")
                })
                """

            return {
                'name': 'Sorgu Sonucu',
                'type': 'ir.actions.act_window',
                'res_model': 'eprescription.list.query.wizard',
                'target': 'new',
                'view_mode': 'form',
                'context': {
                    'default_patient_name': self.patient_id.name,
                    'default_patient_surname': self.patient_id.surname,
                    'default_eprescriptions_list': [(4, epre.id) for epre in self.eprescriptions_list]
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
                    'default_sonuc_kodu': erecete.sonucKodu,
                    'default_sonuc_mesaji': erecete.sonucMesaji,
                }
            }
