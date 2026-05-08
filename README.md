# Product Variant Fixed Price

[![Odoo](https://img.shields.io/badge/Odoo-19.0-714B67)](https://www.odoo.com/)
[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

Replace Odoo's default *additive* variant pricing (template list price + price
extra) with an **absolute fixed price per attribute value**.

## Why

Out of the box Odoo computes the sales price of a product variant as:

```
variant.lst_price = template.list_price + sum(attribute_value.price_extra)
```

That model works well when each attribute value is a *surcharge* on top of a
base product, but it forces back-office users to do mental arithmetic
(`base + Δ`) every time they want to set a final price. For shops where each
variant simply *has* a price, the additive model gets in the way and is
error-prone (changing the template price silently shifts every variant).

This module flips the model: each attribute value can carry an **absolute
price**, and the variant's sales price becomes the sum of those fixed prices.
When no fixed price is set, the standard Odoo behaviour is preserved, so the
module is safe to install on existing databases.

## Features

- New `Fixed Price` field on `product.template.attribute.value`, exposed in
  the **Attributes & Variants** tab on the product template form.
- New computed `Variant Fixed Price` and `Has Fixed Variant Price` fields on
  `product.product`, displayed on the variant form when applicable.
- Variant `lst_price`, pricelist `_compute_base_price` and sale order line
  `price_unit` all pick up the fixed price automatically.
- Pricelists keep working unchanged — they operate on top of the new base
  price, so percentage / formula rules behave exactly as before.
- Backwards compatible fallback: variants with no `fixed_price` configured
  follow the standard `list_price + price_extra` calculation.
- One-shot data migration on installation: existing `price_extra` values are
  copied to `fixed_price` so every variant keeps the same final price.
- Translations in Swedish, Norwegian Bokmål, Danish and Finnish.

## Compatibility

- Odoo 19.0 Community / Enterprise.
- Depends on `product` and `sale_management`.

## Installation

1. Clone the repository and check out the `19.0` branch:

   ```bash
   git clone -b 19.0 https://github.com/drzaphod85/product_variant_fixed_price.git
   ```

2. Add the parent folder to your Odoo `addons_path`.

3. Update the apps list and install **Product Variant Fixed Price** from the
   Apps menu, or from the command line:

   ```bash
   odoo-bin -c /etc/odoo.conf -d <database> -i product_variant_fixed_price
   ```

   The `post_init_hook` runs automatically on first install and migrates any
   existing `price_extra` values to `fixed_price` (see *Migration* below).

## Usage

### Setting a fixed variant price

1. Open a product template under **Inventory** or **Sales** → **Products**.
2. Go to the **Attributes & Variants** tab and open one of the attribute
   values (e.g. *Size: Large*).
3. Fill in **Fixed Price**. This is the absolute price the variant should
   carry, not a delta.
4. Save. The corresponding `product.product` records will now report the
   configured price as their `Sales Price`.

### Multiple attributes per variant

When a variant is composed of several attribute values that each carry a
fixed price, the values are **summed**. Example:

| Attribute | Value | Fixed Price |
|-----------|-------|-------------|
| Size      | M     | 200         |
| Size      | L     | 220         |
| Color     | Red   | 0           |
| Color     | Blue  | 25          |

- *M / Red* → `200 + 0 = 200`
- *L / Blue* → `220 + 25 = 245`

For products where only one attribute should drive the price, leave the
fixed price at `0` on the other attribute's values; they will contribute
nothing to the total.

### Falling back to the legacy behaviour

If **no** attribute value of a variant has a `fixed_price > 0`, the variant
is priced the standard way (`template.list_price + sum(price_extra)`). This
makes it possible to migrate gradually: convert one product family at a
time without breaking the rest of the catalogue.

## Migration on install

The `post_init_migrate_price_extra` hook runs once on first install. For
every `product.template.attribute.value` whose `price_extra` is not zero,
the hook sets:

```
fixed_price = product_tmpl_id.list_price + price_extra
```

This keeps the final selling price of every existing variant unchanged. The
hook never overwrites a `fixed_price` that has already been set (default
value `0.0`), so re-installing the module is safe.

## How it works under the hood

| Layer | What this module changes |
|---|---|
| `product.template.attribute.value` | New `fixed_price` Float field. |
| `product.product._compute_product_lst_price` | Returns `sum(fixed_price)` when any attribute value has it set, otherwise calls `super()`. |
| `product.product._price_compute('list_price', …)` | Same substitution, applied at the entry point used by pricelists, the website and sale order lines. |
| `sale.order.line._compute_price_unit` | Extra `@api.depends` so draft order lines recompute when an attribute value's `fixed_price` is edited later. |
| Views | `fixed_price` exposed next to `price_extra`; `fixed_price_total` shown on the variant form. |

Pricelists are **not** bypassed — when a pricelist rule applies, it
operates on top of the fixed price exactly the way it would on top of
`list_price + price_extra` today.

## Languages

Translations are bundled for:

- 🇸🇪 Swedish (`sv`)
- 🇳🇴 Norwegian Bokmål (`nb_NO`)
- 🇩🇰 Danish (`da`)
- 🇫🇮 Finnish (`fi`)

Install or activate the desired language from **Settings → Translations →
Languages** to see translated field labels and help texts.

## Module structure

```
product_variant_fixed_price/
├── __init__.py
├── __manifest__.py
├── hooks.py
├── i18n/
│   ├── product_variant_fixed_price.pot
│   ├── sv.po
│   ├── nb_NO.po
│   ├── da.po
│   └── fi.po
├── models/
│   ├── __init__.py
│   ├── product_product.py
│   ├── product_template_attribute_value.py
│   └── sale_order_line.py
├── views/
│   └── product_attribute_views.xml
└── README.md
```

## Known limitations

- The fixed price is summed across attribute values. For a product with two
  pricing-relevant attributes, you must decide which one carries the price
  and leave the other at `0` (or distribute the price between them). This
  is by design — modelling a price *matrix* per combination is out of scope.
- Cost (`standard_price`) is not affected.
- The website / e-commerce configurator inherits the new behaviour through
  `_price_compute`, but custom themes that hard-code `list_price +
  price_extra` may need to be updated.

## Contributing

Bug reports and pull requests are welcome on the GitHub repository. Please
target the `19.0` branch.

When adding translatable strings, regenerate the template file:

```bash
odoo-bin -c /etc/odoo.conf -d <database> --i18n-export=i18n/product_variant_fixed_price.pot --modules=product_variant_fixed_price
```

and merge the new strings into the existing `.po` files with `msgmerge`.

## License

This module is released under the **LGPL-3.0** license. See the
[LICENSE](LICENSE) file for the full text.

## Credits

- **Author:** Familjen Larsson
- **Maintainer:** Lasse Larsson — <lasse@familjenlarsson.eu>
