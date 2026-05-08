from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    has_fixed_price = fields.Boolean(
        string="Has Fixed Variant Price",
        compute="_compute_fixed_price_total",
        help=(
            "Technical flag, true when at least one of the variant's "
            "attribute values has a fixed price greater than zero."
        ),
    )
    fixed_price_total = fields.Float(
        string="Variant Fixed Price",
        compute="_compute_fixed_price_total",
        digits="Product Price",
        help=(
            "Sum of the fixed prices of the attribute values that compose "
            "this variant. Only attribute values with fixed_price > 0 are "
            "summed; the others contribute zero to this total."
        ),
    )

    @api.depends(
        "product_template_attribute_value_ids",
        "product_template_attribute_value_ids.fixed_price",
    )
    def _compute_fixed_price_total(self):
        for product in self:
            priced_values = product.product_template_attribute_value_ids.filtered(
                lambda v: v.fixed_price > 0
            )
            product.has_fixed_price = bool(priced_values)
            product.fixed_price_total = sum(priced_values.mapped("fixed_price"))

    @api.depends(
        "list_price",
        "price_extra",
        "product_template_attribute_value_ids.fixed_price",
    )
    @api.depends_context("uom")
    def _compute_product_lst_price(self):
        # Run the standard computation first so non-fixed-price variants and
        # all other side effects (currency, uom conversion, etc.) keep working.
        super()._compute_product_lst_price()

        to_uom = None
        if "uom" in self.env.context:
            to_uom = self.env["uom.uom"].browse(self.env.context["uom"])

        for product in self:
            priced_values = product.product_template_attribute_value_ids.filtered(
                lambda v: v.fixed_price > 0
            )
            if not priced_values:
                # No fixed price configured: keep the standard list_price + extra.
                continue
            price = sum(priced_values.mapped("fixed_price"))
            if to_uom and product.uom_id and to_uom != product.uom_id:
                price = product.uom_id._compute_price(price, to_uom)
            product.lst_price = price

    def _price_compute(
        self,
        price_type,
        fiscal_position=False,
        currency=None,
        uom=None,
        company=False,
        date=False,
    ):
        """Make the fixed price the source of truth for ``list_price`` lookups.

        ``product.product._price_compute`` is the entry point used by
        pricelists, sale order lines and the website to evaluate a product's
        list price. The standard implementation reads
        ``product.list_price + product.price_extra``; we substitute the
        configured fixed price when it is set so pricelist rules computed on
        top of the list price use the right base.
        """
        prices = super()._price_compute(
            price_type,
            fiscal_position=fiscal_position,
            currency=currency,
            uom=uom,
            company=company,
            date=date,
        )

        if price_type != "list_price":
            return prices

        company = company or self.env.company
        date = date or fields.Date.context_today(self)

        for product in self:
            priced_values = product.product_template_attribute_value_ids.filtered(
                lambda v: v.fixed_price > 0
            )
            if not priced_values:
                continue
            price = sum(priced_values.mapped("fixed_price"))
            if uom and product.uom_id and uom != product.uom_id:
                price = product.uom_id._compute_price(price, uom)
            target_currency = currency or product.currency_id
            if target_currency and product.currency_id and target_currency != product.currency_id:
                price = product.currency_id._convert(
                    price, target_currency, company, date,
                )
            prices[product.id] = price

        return prices
