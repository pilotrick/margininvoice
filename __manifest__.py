# -*- coding: utf-8 -*-

{
    'name': 'Margins in Account Invoice',
    'version':'1.0',
    'category': 'Accounting',
    'description': """
This module adds the 'Margin' on Invoice.
=============================================

This gives the profitability by calculating the difference between the Unit
Price and Cost Price.
    """,
    'depends':['account'],
    'data':['views/account_invoice_margin_view.xml'],
}
