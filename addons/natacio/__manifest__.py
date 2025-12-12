# -*- coding: utf-8 -*-
{
    'name': "Natació Federació",

    'summary': "Gestió de clubs, categories, nadadors i campionats de natació",

    'description': """
    Mòdul de gestió per a la Federació de Natació:
    - Clubs amb nadadors i classificacions.
    - Categories d'edat i estils de natació.
    - Campionats amb sessions, proves i resultats.
    - Control de quotes anuals i participació.
    """,

    'author': "Federació de Natació",
    'website': "https://www.federacionnatacio.local",

    'category': 'Sports',
    'depends': [
        'base',
        'contacts',
        'mail',
    ],

    'data': [   
        # Seguridad
        'security/ir.model.access.csv',

        # Primero las acciones y vistas
        'views/club_views.xml',
        'views/category_views.xml',
        'views/swimmer_views.xml',
        'views/style_views.xml',
        'views/championship_views.xml',
        'views/session_views.xml',
        'views/event_views.xml',
        'views/series_views.xml',
        'views/result_views.xml',

        # Menús
        'views/natacio_menus.xml',
    ],

    'demo': [
        'demo/demo.xml',  # Aquí se especifica la ruta correcta
    ],

    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
