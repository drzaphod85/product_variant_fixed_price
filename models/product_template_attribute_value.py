from odoo import api, fields, models


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
            "price.\n\n"
            "When every variant of the template has a fixed price, the "
            "template's own Sales Price is automatically kept in sync with "
            "the cheapest variant so the e-commerce listing matches the "
            "product page."
        ),
    )

    # ------------------------------------------------------------------
    # CRUD overrides: keep template.list_price in sync with the cheapest
    # priced variant whenever fixed_price changes. The sync itself lives
    # on product.template (_sync_list_price_from_variants); these hooks
    # just make sure it is called at the right moments.
    #
    # A skip_fixed_price_sync context flag is honoured for batch operations
    # (e.g. the post-install migration) where the sync should run once at
    # the end rather than per-write.
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get("skip_fixed_price_sync") and any(
            "fixed_price" in vals for vals in vals_list
        ):
            records.product_tmpl_id._sync_list_price_from_variants()
        return records

    def write(self, vals):
        result = super().write(vals)
        if "fixed_price" in vals and not self.env.context.get(
            "skip_fixed_price_sync"
        ):
            self.product_tmpl_id._sync_list_price_from_variants()
        return result

    def unlink(self):
        templates = self.mapped("product_tmpl_id")
        result = super().unlink()
        remaining = templates.exists()
        if remaining and not self.env.context.get("skip_fixed_price_sync"):
            remaining._sync_list_price_from_variants()
        return result
