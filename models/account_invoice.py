# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "account.move.line"

    margin = fields.Float(
        "Margin", compute='_compute_margin',
        digits='Product Price', store=True, groups="base.group_user")
    margin_percent = fields.Float(
        "Margin (%)", compute='_compute_margin', store=True, groups="base.group_user")
    purchase_price = fields.Float(
        string='Cost', compute="_compute_purchase_price",
        digits='Product Price', store=True, readonly=False,
        groups="base.group_user")

    @api.depends('product_id', 'company_id', 'currency_id', 'product_uom_id')
    def _compute_purchase_price(self):
        for line in self:
            if not line.product_id:
                line.purchase_price = 0.0
                continue
            line = line.with_company(line.company_id)
            product = line.product_id
            product_cost = product.standard_price
            if not product_cost:
                line.purchase_price = 0.0
                continue
            fro_cur = product.cost_currency_id
            to_cur = line.currency_id or line.move_id.currency_id
            if line.product_uom_id and line.product_uom_id != product.uom_id:
                product_cost = product.uom_id._compute_price(
                    product_cost,
                    line.product_uom_id,
                )
            line.purchase_price = fro_cur._convert(
                from_amount=product_cost,
                to_currency=to_cur,
                company=line.company_id or self.env.company,
                date=line.move_id.invoice_date or fields.Date.today(),
                round=False,
            ) if to_cur and product_cost else product_cost

    @api.depends('price_subtotal', 'quantity', 'purchase_price')
    def _compute_margin(self):
        for line in self:
            line.margin = line.price_subtotal - (line.purchase_price * line.quantity)
            line.margin_percent = line.price_subtotal and line.margin/line.price_subtotal


class SaleOrder(models.Model):
    _inherit = "account.move"

    margin = fields.Monetary("Margin", compute='_compute_margin', store=True)
    margin_percent = fields.Float("Margin (%)", compute='_compute_margin', store=True)

    @api.depends('invoice_line_ids.margin', 'amount_untaxed')
    def _compute_margin(self):
        if not all(self._ids):
            for move in self:
                move.margin = sum(move.invoice_line_ids.mapped('margin'))
                move.margin_percent = move.amount_untaxed and move.margin/move.amount_untaxed
        else:
            self.env["account.move.line"].flush(['margin'])
            for move in self:
                move.margin = sum(move.invoice_line_ids.mapped('margin'))
                move.margin_percent = move.amount_untaxed and move.margin/move.amount_untaxed
