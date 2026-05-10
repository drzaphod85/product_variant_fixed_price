# Changelog

All notable changes to **Product Variant Fixed Price** are documented in this
file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to the Odoo module versioning scheme
`<odoo-version>.<major>.<minor>.<patch>` (e.g. `19.0.1.0.0`).

## [Unreleased]

## [19.0.2.0.0] - 2026-05-10

### Changed

- **Architecture switch.** Instead of overriding the e-commerce
  rendering path to substitute the cheapest variant's price at display
  time, the module now keeps `template.list_price` automatically synced
  to `min(variant.lst_price)` whenever every variant of the template
  has a `fixed_price` configured. This produces the correct price in
  every Odoo view (shop list, product page, POS, sales orders,
  configurator, snippets, exported reports, etc.) without per-view
  overrides.
- A new computed boolean `product.template.has_priced_variants` flags
  templates that fall under the auto-sync rule. When it is true,
  `list_price` is rendered read-only on the product template form to
  prevent the user from desynchronising the field manually.
- The `_sync_list_price_from_variants` method on `product.template`
  intentionally skips templates that mix `fixed_price` and the standard
  `price_extra` mechanism. Lowering `list_price` would otherwise also
  lower the price of every variant that relies on
  `template.list_price + price_extra`. The "all-or-nothing" rule lets
  the two pricing modes coexist cleanly in the same database.

### Added

- New CRUD hooks on `product.template.attribute.value` (create / write
  / unlink) that trigger the sync when `fixed_price` changes. A
  `skip_fixed_price_sync` context flag allows batch operations (e.g.
  the post-install migration) to defer the sync until the end.
- View inherit: `list_price` on the product template form is marked
  `readonly="has_priced_variants"` and the helper field is added to
  the form data context.
- Module icon (`static/description/icon.svg` and `icon.png`): a price
  tag with an equals sign over an Odoo-purple background and three
  variant-colour dots, signalling "absolute price per variant" rather
  than "extra added to the template price".

### Removed

- `product.template._price_compute('list_price', ...)` override (no
  longer necessary; the synced `list_price` is the right value).
- `product.template._get_combination_info` override (same reason).
- The defensive `sale.order.line` import is kept as a documentation
  stub but contains no behaviour.

### Migration

- Existing installations are upgraded automatically: after running
  `-u product_variant_fixed_price`, the post-install hook re-runs the
  sync once for every template whose attribute values were migrated
  from `price_extra`.
- Stores that were partially relying on the previous display override
  for templates with mixed fixed_price / price_extra variants will
  fall back to the standard Odoo display (template list_price) for
  those templates. To get the cheapest-variant display back, fill in
  `fixed_price` on every variant's attribute values so the sync rule
  applies.

## [19.0.1.1.1] - 2026-05-08

### Fixed

- The shop list (`/shop`) still showed `0,00 kr` on templates priced at
  the variant level. The previous release (`19.0.1.1.0`) only overrode
  `_get_combination_info`, but Odoo 19's website actually goes through
  `product.template._get_sales_prices` -> `template._price_compute('list_price')`
  for the shop card. A new override on `product.template._price_compute`
  now substitutes the cheapest priced variant's price at that upstream
  call, so the card matches the product page.
- `_get_combination_info` override forwarded `only_template=True` into
  the second `super()` call, which made the parent ignore the variant
  `product_id` and fall back to template-level pricing (defeating the
  whole point of the override). The flag is now stripped from the
  forwarded kwargs.

## [19.0.1.1.0] - 2026-05-08

### Added

- `product.template._get_combination_info` override that aligns the
  e-commerce shop list price with the product detail page. When the
  template-level call is made (no specific variant requested) and at
  least one variant of the template has a `fixed_price > 0`, the
  cheapest priced variant is used to compute `price` / `list_price` /
  `has_discounted_price`. Display name, image and `product_template_id`
  are kept untouched, so the shop card still shows the template — just
  with the cheapest variant's price.
- New `models/product_template.py` module file.

### Notes

- Standard Odoo behaviour is preserved when no variant of the template
  has a fixed price set, or when a specific combination / variant is
  requested by the caller (POS, sale order, configurator).

## [19.0.1.0.1] - 2026-05-08

### Fixed

- `ProductProduct._price_compute` now uses a generic `*args, **kwargs`
  signature so it forwards the keyword arguments that the Odoo 19 parent
  method actually accepts. The previous explicit signature carried over
  `fiscal_position` and `company` from older Odoo versions and raised
  `TypeError: _price_compute() got an unexpected keyword argument
  'fiscal_position'` whenever the website snippet, a pricelist rule or any
  other caller exercised the override.

### Changed

- Removed the `sale.order.line._compute_price_unit` override. Re-declaring
  `@api.depends` on an inherited compute method silently replaces the
  parent's dependency list, which broke recompute triggers on product /
  quantity / pricelist changes. The fixed price still flows into
  `price_unit` automatically through the overridden
  `product.product._price_compute('list_price')`, so no replacement
  override is needed.

## [19.0.1.0.0] - 2026-05-08

### Added

- New `Fixed Price` field on `product.template.attribute.value` for setting
  an absolute sales price per attribute value.
- Computed `Variant Fixed Price` (`fixed_price_total`) and
  `Has Fixed Variant Price` (`has_fixed_price`) fields on `product.product`.
- Override of `product.product._compute_product_lst_price` and
  `_price_compute('list_price', …)` so the fixed price flows through to
  variant `lst_price`, pricelists, the website and sale order lines.
- Extended `sale.order.line._compute_price_unit` dependency graph so draft
  order lines recompute when an attribute value's `fixed_price` is edited.
- View inheritance to expose `fixed_price` next to `price_extra` on the
  attribute value form, and to display `fixed_price_total` on the variant
  form when applicable.
- `post_init_migrate_price_extra` hook that copies existing `price_extra`
  values into `fixed_price` (`fixed_price = template.list_price + price_extra`)
  on first install, preserving the final selling price of every existing
  variant.
- Translations: Swedish (`sv`), Norwegian Bokmål (`nb_NO`), Danish (`da`),
  Finnish (`fi`).

### Notes

- Fully backwards compatible: variants whose attribute values all keep
  `fixed_price = 0` continue to use the standard
  `template.list_price + price_extra` calculation.
- Pricelist rules are not bypassed; they are evaluated on top of the new
  base price.

[Unreleased]: https://github.com/drzaphod85/product_variant_fixed_price/compare/19.0.2.0.0...19.0
[19.0.2.0.0]: https://github.com/drzaphod85/product_variant_fixed_price/compare/19.0.1.1.1...19.0.2.0.0
[19.0.1.1.1]: https://github.com/drzaphod85/product_variant_fixed_price/compare/19.0.1.1.0...19.0.1.1.1
[19.0.1.1.0]: https://github.com/drzaphod85/product_variant_fixed_price/compare/19.0.1.0.1...19.0.1.1.0
[19.0.1.0.1]: https://github.com/drzaphod85/product_variant_fixed_price/compare/19.0.1.0.0...19.0.1.0.1
[19.0.1.0.0]: https://github.com/drzaphod85/product_variant_fixed_price/releases/tag/19.0.1.0.0
