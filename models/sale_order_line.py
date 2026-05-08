"""Sale order line integration documentation.

Pricing flows from a configured ``fixed_price`` into ``sale.order.line``
through the standard Odoo chain:

    sale.order.line._get_display_price
        -> _get_pricelist_price
        -> product.pricelist.item._compute_price
        -> _compute_base_price
        -> product.product._price_compute('list_price')

Because :meth:`product.product._price_compute` is overridden in
``product_product.py`` to return the configured fixed price when it is set,
every freshly added or recomputed sale order line automatically picks up
the variant fixed price as its base price (before any pricelist discount
or markup is applied). No additional override of ``sale.order.line`` is
required.

If a fixed price is edited after a draft order line has already been
created, the line will only reflect the new price the next time
``price_unit`` is recomputed (for example by re-selecting the product on
the line or by triggering "Update prices" on the order). This matches
Odoo's standard behaviour for any product price change.
"""

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Intentionally empty: the integration is handled entirely through
    # product.product._price_compute. The class is kept so the module
    # explicitly declares its touchpoint with sale.order.line and can be
    # extended here in future versions without restructuring imports.
