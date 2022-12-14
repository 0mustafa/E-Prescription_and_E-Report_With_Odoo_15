# -*- coding: utf8 -*-
import datetime

from odoo import models, fields, api


class QueryEprescriptionListWizard(models.TransientModel):

    _name = "eprescription.list.query.wizard"
    _description = "E-Reçete Listesi Wizard"

    patient_name = fields.Char(string="Hasta Adı")
    patient_surname = fields.Char(string="Hasta Soyadı")
    eprescriptions_list = fields.Many2many('hospital.eprescription', string="Hastaya ait e-reçeteler")
