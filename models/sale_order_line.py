"""Sale order line integration for the variant fixed price.

The unit price on a ``sale.order.line`` is computed by Odoo through
``sale.order.line._get_display_price`` -> ``_get_pricelist_price`` ->
``product.pricelist.item._compute_price`` -> ``_compute_base_price`` ->
``product.product._price_compute('list_price')``.

Because :meth:`product.product._price_compute` is already overridden in
``product_product.py`` to return the configured ``fixed_price`` when it is
set, every freshly added sale order line automatically picks up the variant
fixed price as its base price (before any pricelist discount or markup is
applied).

The override below only adds an explicit recompute trigger so that draft
order lines update their unit price when an attribute value's fixed price is
edited after the line was created.
"""

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "product_id.product_template_attribute_value_ids.fixed_price",
    )
    def _compute_price_unit(self):
        # Delegate the actual computation to the standard implementation; we
        # only extend the dependency graph so that updating ``fixed_price`` on
        # an attribute value invalidates and recomputes any draft order line
        # that uses the affected variant.
        return super()._compute_price_unit()
