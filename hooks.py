"""Post-install migration hook for product_variant_fixed_price.

Two responsibilities:

1. Copy existing ``price_extra`` values into the new ``fixed_price`` field
   so variants keep the same final selling price after installation. For
   every ``product.template.attribute.value`` whose ``price_extra`` is not
   zero, ``fixed_price`` is set to ``template.list_price + price_extra``.

2. Trigger ``_sync_list_price_from_variants`` once on every affected
   template so that ``template.list_price`` is aligned with the cheapest
   variant whenever every variant has a fixed price configured. The
   per-write sync that lives on ``product.template.attribute.value`` is
   suppressed during the migration with the ``skip_fixed_price_sync``
   context flag and replaced by a single batched call at the end.
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

    affected_templates = env["product.template"]
    migrated = 0

    # Suppress the per-write sync; we run it once below for the whole batch.
    values_silent = values.with_context(skip_fixed_price_sync=True)
    for value in values_silent:
        template = value.product_tmpl_id
        if not template:
            continue
        # Only migrate when the field is still at its default to avoid
        # overwriting any value the user may have set during installation.
        if value.fixed_price != 0.0:
            continue
        value.fixed_price = template.list_price + value.price_extra
        affected_templates |= template
        migrated += 1

    if affected_templates:
        affected_templates._sync_list_price_from_variants()

    _logger.info(
        "product_variant_fixed_price: migrated %s attribute value(s) "
        "from price_extra to fixed_price; synced %s template(s).",
        migrated,
        len(affected_templates),
    )
