from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _price_compute(self, price_type, *args, **kwargs):
        """Substitute the cheapest variant's fixed price for the template.

        ``product.template._price_compute('list_price')`` is the upstream
        method called by every place that asks "what does this template
        cost?" — including ``website_sale`` ``_get_sales_prices`` (the
        actual ``/shop`` page), the price-range filter slider and the
        category snippets.

        Out of the box it returns ``template.list_price``, which is
        usually zero on stores that price at the variant level. We
        substitute the lowest priced variant's ``_price_compute('list_price')``
        result when at least one variant of the template has a
        ``fixed_price > 0``. The variant call goes through
        :meth:`product.product._price_compute` which already handles the
        fixed-price substitution and any uom / currency context.
        """
        prices = super()._price_compute(price_type, *args, **kwargs)

        if price_type != "list_price":
            return prices

        for template in self:
            priced_variants = template.product_variant_ids.filtered(
                lambda p: p.has_fixed_price
            )
            if not priced_variants:
                continue
            cheapest = min(priced_variants, key=lambda p: p.lst_price)
            variant_prices = cheapest._price_compute(
                price_type, *args, **kwargs
            )
            if cheapest.id in variant_prices:
                prices[template.id] = variant_prices[cheapest.id]

        return prices

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        *args,
        **kwargs,
    ):
        """Show the cheapest fixed-price variant on template-level views.

        This complements the :meth:`_price_compute` override by also
        handling the cases where ``_get_combination_info`` is called
        without a specific variant — namely the e-commerce category
        snippets and the configurator's default state.

        Standard behaviour is preserved when:
          * a specific ``combination`` or ``product_id`` is requested
            (the variant's own price is already correct via
            :meth:`product.product._price_compute`), or
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

        cheapest = min(priced_variants, key=lambda p: p.lst_price)

        # Drop ``only_template`` from the keyword arguments forwarded to
        # the second ``super()`` call. With ``only_template=True`` the
        # parent method ignores the variant ``product_id`` and falls back
        # to template-level pricing — which is exactly the value we are
        # trying to override here.
        variant_kwargs = {
            k: v for k, v in kwargs.items() if k != "only_template"
        }

        cheapest_info = super()._get_combination_info(
            combination=cheapest.product_template_attribute_value_ids,
            product_id=cheapest.id,
            *args,
            **variant_kwargs,
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
