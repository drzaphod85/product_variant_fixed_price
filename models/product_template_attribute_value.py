from odoo import fields, models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    fixed_price = fields.Float(
        string="Fixed Price",
        digits="Product Price",
        default=0.0,
        help=(
            "Absolute sales price for variants that include this attribute "
            "value. When set (greater than zero) it replaces the default "
            "behaviour of adding the template's list price and the price "
            "extra. If multiple attribute values on the same variant have a "
            "fixed price, the values are summed to compute the final variant "
            "price."
        ),
    )
