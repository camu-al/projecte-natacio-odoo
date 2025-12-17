# -*- coding: utf-8 -*-
{
    'name': "Natació Federació",

    'depends': [
        'base',
        'contacts',
        'mail',
    ],

    'data': [   
        # Security
        'security/ir.model.access.csv',

        # Views
        'views/club_views.xml',
        'views/category_views.xml',
        'views/swimmer_views.xml',
        'views/style_views.xml',
        'views/championship_views.xml',
        'views/session_views.xml',
        'views/event_views.xml',
        'views/series_views.xml',
        'views/result_views.xml',

        # Menus
        'views/natacio_menus.xml',
    ],

    'demo': [
        'demo/demo.xml',  
    ],

    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
