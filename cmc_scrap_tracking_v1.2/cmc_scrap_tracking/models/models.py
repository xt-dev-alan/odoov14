# -*- coding: utf-8 -*-

from odoo import models, fields, api


# Adding fields to product.teamplate
class cmc_product(models.Model):
    _inherit = 'product.template'
    # Model fields
    cmc_container_type_ids = fields.Many2one('container_types', string="Container")


# Container Types on Product screnn for Containers
class cmc_container_types(models.Model):
    _name = 'container_types'
    _description = 'Container Types'
    # Model fields
    name = fields.Char("Carrier Type")
    product_ids = fields.One2many('product.template', 'cmc_container_type_ids')


# Adding fields for Container tracking and weights on Lots
class cmc_lot_container(models.Model):
    _inherit = 'stock.production.lot'
    # Additional Model Fields
    cmc_container = fields.Many2one('product.template', string="Container")
    cmc_tare_weight = fields.Float(related='cmc_container.weight', string="Tare Weight")
    cmc_net_weight = fields.Float("Net Weight", compute='_compute_net')

    # Calculating Net Weight
    @api.depends('product_qty', 'cmc_container.weight', 'quant_ids', '__last_update')
    def _compute_net(self):
        for record in self:
            record.cmc_net_weight = record.product_qty - record.cmc_container.weight


# Adding fields on Inventory Report
class cmc_inventory_report(models.Model):
    _inherit = 'stock.quant'
    # Model fields - Adding related to pull into report
    cmc_lot_container = fields.Many2one(related='lot_id.cmc_container')
    cmc_lot_tare_weight = fields.Float(related='lot_id.cmc_tare_weight')
    cmc_lot_net_weight = fields.Float("Net Weight", compute='_compute_net', store=True)
    cmc_lot_gross_weight = fields.Float(related='lot_id.product_qty', string='Gross Weight')
    product_category = fields.Many2one(related='product_id.categ_id')

    @api.depends('inventory_quantity', 'lot_id.cmc_tare_weight')
    def _compute_net(self):
        for record in self:
            record.cmc_lot_net_weight = record.inventory_quantity - record.cmc_lot_tare_weight


# Adding fields on Operations
# Should show just for Shipments Out
class cmc_shipping(models.Model):
    _inherit = 'stock.picking'
    # Model fields
    cmc_load_date = fields.Date("Load Date")
    cmc_ship_date = fields.Date("Ship Date")
    cmc_truck_nbr = fields.Char("Truck Number")
    cmc_trailer_number = fields.Char("Trailer Number")
    cmc_seal_number = fields.Char("Seal Number")
    cmc_carrier_ids = fields.Many2one('cmc_carriers', string="Carrier")
    type_of_operation = fields.Selection(related='picking_type_id.code')
    cmc_shipment_customer_id = fields.Many2one('res.partner', string="Customer")


# Link to Contact(Customer)
class cmc_customer(models.Model):
    _inherit = 'res.partner'
    cmc_shipments = fields.One2many('stock.picking', 'cmc_shipment_customer_id', 'Shipments')


# Carrier List
class cmc_carriers(models.Model):
    _name = 'cmc_carriers'
    _description = 'Carriers'
    # Model fields
    name = fields.Char("Carrier ID")
    description = fields.Char("Carrier Name")
    shipment_ids = fields.One2many('stock.picking', 'cmc_carrier_ids')
