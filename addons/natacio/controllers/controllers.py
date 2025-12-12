# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class NatacioController(http.Controller):

    @http.route('/natacio/championships', auth='public', type='json')
    def get_championships(self):
        """Devuelve todos los campionats con sus datos básicos y ranking"""
        champs = request.env['natacio.championship'].sudo().search([])
        data = []
        for c in champs:
            data.append({
                'id': c.id,
                'name': c.name,
                'date_start': c.date_start,
                'date_end': c.date_end,
                'clubs': [(club.id, club.name) for club in c.club_ids],
                'swimmers': [(sw.id, sw.name) for sw in c.swimmer_ids],
                'ranking': c.ranking,
            })
        return data

    @http.route('/natacio/championships/<int:champ_id>/results', auth='public', type='json')
    def get_championship_results(self, champ_id):
        """Devuelve todos los resultados de un campionat"""
        champ = request.env['natacio.championship'].sudo().browse(champ_id)
        if not champ:
            return {'error': 'Campionat no trobat'}
        results = []
        for session in champ.session_ids:
            for event in session.event_ids:
                for result in event.result_ids:
                    results.append({
                        'event': event.name,
                        'swimmer': result.swimmer_id.name,
                        'club': result.club_id.name,
                        'time': result.time,
                        'points': result.points,
                        'series': result.series_id.name if result.series_id else None,
                    })
        return results
