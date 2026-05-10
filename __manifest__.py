{
    "name": "Product Variant Fixed Price",
    "version": "19.0.1.1.0",
    "summary": (
        "Set an absolute (fixed) sales price per product variant attribute "
        "value instead of an extra amount added on top of the template price."
    ),
    "description": """
Product Variant Fixed Price
===========================

By default Odoo computes the sales price of a product variant as
``product.template.list_price`` plus a *price extra* defined on each
``product.template.attribute.value``.

This module introduces a new ``Fixed Price`` field on the attribute value.
When the field is set (greater than zero), the variant's sales price becomes
the sum of the fixed prices of its attribute values, completely replacing
the additive behaviour. When no attribute value of a variant has a fixed
price, the standard Odoo behaviour (template list price + price extra) is
preserved, so the module is fully backwards compatible.

On installation, existing ``price_extra`` values are migrated to the new
``fixed_price`` field (``fixed_price = template.list_price + price_extra``)
so the final selling price of every existing variant remains unchanged.
    """,
    "author": "Familjen Larsson",
    "website": "https://familjenlarsson.eu",
    "license": "LGPL-3",
    "category": "Sales/Sales",
    "depends": [
        "product",
        "sale_management",
    ],
    "data": [
        "views/product_attribute_views.xml",
    ],
    "post_init_hook": "post_init_migrate_price_extra",
    "installable": True,
    "application": False,
}
