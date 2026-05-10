from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    has_priced_variants = fields.Boolean(
        string="Has Variant Fixed Prices",
        compute="_compute_has_priced_variants",
        help=(
            "True when every variant of this template has a fixed_price "
            "(> 0) configured on its attribute values. While true, the "
            "template's Sales Price (list_price) is auto-synced to the "
            "cheapest variant's price and the field is shown read-only on "
            "the form."
        ),
    )

    @api.depends(
        "product_variant_ids",
        "product_variant_ids.has_fixed_price",
    )
    def _compute_has_priced_variants(self):
        for template in self:
            variants = template.product_variant_ids
            template.has_priced_variants = bool(variants) and all(
                v.has_fixed_price for v in variants
            )

    def _sync_list_price_from_variants(self):
        """Set list_price = min(variant.lst_price) for templates whose
        variants all carry a fixed_price.

        The sync is intentionally skipped for templates that mix fixed_price
        and the standard price_extra mechanism. Lowering the template's
        list_price would also lower the lst_price of variants that rely on
        ``template.list_price + price_extra``, which is almost certainly
        not what the user wants. The "all or nothing" rule lets the two
        modes coexist on the same database without surprising regressions.

        The sync is also a no-op when the template has no variants at all
        (a single-product template never benefits from variant-level
        pricing) or when the computed minimum already matches the current
        list_price.
        """
        for template in self:
            variants = template.product_variant_ids
            if not variants:
                continue
            if not all(v.has_fixed_price for v in variants):
                continue
            new_price = min(variants.mapped("lst_price"))
            if template.list_price != new_price:
                template.list_price = new_price
