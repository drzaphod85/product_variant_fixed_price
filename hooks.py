"""Post-install migration hook for product_variant_fixed_price.

Copies existing ``price_extra`` values into the new ``fixed_price`` field so
that variants keep the same final selling price after installation.

For every ``product.template.attribute.value`` whose ``price_extra`` is not
zero, ``fixed_price`` is set to ``template.list_price + price_extra``. This
matches the price that the variant would have produced before the module
took over the price computation, preserving backwards compatibility for
existing data.
"""

import logging

_logger = logging.getLogger(__name__)


def post_init_migrate_price_extra(env):
    Ptav = env["product.template.attribute.value"]
    values = Ptav.search([("price_extra", "!=", 0)])
    if not values:
        _logger.info(
            "product_variant_fixed_price: no price_extra values to migrate."
        )
        return

    migrated = 0
    for value in values:
        template = value.product_tmpl_id
        if not template:
            continue
        new_price = template.list_price + value.price_extra
        # Only migrate when the field is still at its default to avoid
        # overwriting any value the user may have set during installation.
        if value.fixed_price == 0.0:
            value.fixed_price = new_price
            migrated += 1

    _logger.info(
        "product_variant_fixed_price: migrated %s attribute value(s) "
        "from price_extra to fixed_price.",
        migrated,
    )
