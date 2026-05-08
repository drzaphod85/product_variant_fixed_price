# Changelog

All notable changes to **Product Variant Fixed Price** are documented in this
file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to the Odoo module versioning scheme
`<odoo-version>.<major>.<minor>.<patch>` (e.g. `19.0.1.0.0`).

## [Unreleased]

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

[Unreleased]: https://github.com/drzaphod85/product_variant_fixed_price/compare/19.0.1.0.1...19.0
[19.0.1.0.1]: https://github.com/drzaphod85/product_variant_fixed_price/compare/19.0.1.0.0...19.0.1.0.1
[19.0.1.0.0]: https://github.com/drzaphod85/product_variant_fixed_price/releases/tag/19.0.1.0.0
