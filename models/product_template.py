from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        *args,
        **kwargs,
    ):
        """Show the cheapest fixed-price variant on template-level views.

        Out of the box, the e-commerce shop list (and any other view that
        asks "what does this template cost?") returns ``template.list_price``
        whenever ``_get_combination_info`` is called without a specific
        variant. The product detail page, on the other hand, defaults to
        the cheapest variant. The two views can therefore display different
        prices for the same product, which is confusing for shoppers.

        When at least one variant of the template has a ``fixed_price > 0``,
        this override forwards the template-level call through the cheapest
        priced variant and copies the resulting price-related keys back
        into the template-level result. Display name, image and
        ``product_template_id`` are kept untouched so the shop card still
        shows the template, just with the cheapest variant's price.

        Standard behaviour is preserved when:
          * a specific ``combination`` or ``product_id`` is requested
            (the variant's own price is already correct via the
            ``_price_compute`` override on ``product.product``), or
          * none of the template's variants has a ``fixed_price > 0``.
        """
        res = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            *args,
            **kwargs,
        )

        if combination or product_id or len(self) != 1:
            return res

        priced_variants = self.product_variant_ids.filtered(
            lambda p: p.has_fixed_price
        )
        if not priced_variants:
            return res

        # ``lst_price`` already accounts for the configured fixed price and
        # any uom / currency context, so it is a faithful proxy for the
        # variant's "starting from" price.
        cheapest = min(priced_variants, key=lambda p: p.lst_price)

        # Re-run the standard logic for the cheapest variant so pricelist
        # rules, taxes-included display and discount flags reflect that
        # variant rather than the template default.
        cheapest_info = super()._get_combination_info(
            combination=cheapest.product_template_attribute_value_ids,
            product_id=cheapest.id,
            *args,
            **kwargs,
        )

        for key in (
            "price",
            "list_price",
            "price_extra",
            "has_discounted_price",
            "compare_list_price",
            "currency_id",
        ):
            if key in cheapest_info:
                res[key] = cheapest_info[key]

        return res
