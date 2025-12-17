# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, timedelta

# ========
# STYLE
# ========
class Style(models.Model):
    _name = "natacio.style"
    _description = "Estil de natació"

    name = fields.Char(string="Nom", required=True)
    top_swimmers = fields.One2many('natacio.swimmer', 'style_id', string="Millors nadadors")

# ============
# CATEGORY
# ===========
class Category(models.Model):
    _name = "natacio.category"
    _description = "Categoria d'edat"

    name = fields.Char(string="Nom", required=True)
    age_min = fields.Integer(string="Edat mínima", required=True)
    age_max = fields.Integer(string="Edat màxima", required=True)

    _sql_constraints = [
        ('age_min_le_max', 'CHECK(age_min <= age_max)', 'La edat mínima ha de ser menor o igual que la màxima.')
    ]

# =======
# CLUB
# =======
class Club(models.Model):
    _name = "natacio.club"
    _description = "Club"

    name = fields.Char(string="Nom", required=True)
    town = fields.Char(string="Poble")
    members_count = fields.Integer(string="Socis", default=0)
    logo = fields.Binary(string="Logo")

    # Relacion un club muchos nadadores
    swimmers_ids = fields.One2many(
        "natacio.swimmer", # modelo donde hace la relacion
         "club_id", # nombre del campo Many2one obligatorio en nadadores
          string="Nadadors") 

    # Relacion muchos clubs muchos campeonatos
    championships_ids = fields.Many2many(
        "natacio.championship",
         string="Campionats")

    total_points = fields.Float(string="Punts totals", compute="_compute_total_points", store=True)

    @api.depends("swimmers_ids.result_ids.points")
    def _compute_total_points(self):
        for club in self:
            club.total_points = sum(r.points for s in club.swimmers_ids for r in s.result_ids)

# ==========
# SWIMMER
# ==========
class Swimmer(models.Model):
    _name = "natacio.swimmer"
    _description = "Nadador"

    name = fields.Char(string="Nom", required=True)
    birth_year = fields.Integer(string="Any de naixement")
    age = fields.Integer(string="Edat", compute="_compute_age", store=True)

    club_id = fields.Many2one("natacio.club", string="Club", ondelete='set null')
    category_id = fields.Many2one("natacio.category", string="Categoria", ondelete='set null')
    style_id = fields.Many2one("natacio.style", string="Estil preferit")
    result_ids = fields.One2many("natacio.result", "swimmer_id", string="Resultats")

    partner_id = fields.Many2one('res.partner', string="Client")
    last_payment_date = fields.Date(string="Últim pagament")
    payment_progress = fields.Float(string="Progrés quota anual", compute="_compute_payment_progress")

    best_times_summary = fields.Text(string="Millors temps per estil", compute="_compute_best_times")

    #Age depende de birth_year al cambiar la fecha calcula la edad
    @api.depends("birth_year") 
    def _compute_age(self):
        year_now = date.today().year #año actual
        for r in self:
            r.age = year_now - r.birth_year if r.birth_year else 0

    @api.depends("last_payment_date")
    def _compute_payment_progress(self):
        today = date.today()
        for r in self:
            if r.last_payment_date:
                end_date = r.last_payment_date + timedelta(days=365)
                days_left = (end_date - today).days
                r.payment_progress = max(0, min(100, days_left / 365 * 100))
            else:
                r.payment_progress = 0

    def register_payment(self):
        for swimmer in self:
            swimmer.last_payment_date = date.today()
            if swimmer.partner_id:
                self.env['sale.order'].create({
                    'partner_id': swimmer.partner_id.id,
                    'order_line': [(0,0,{
                        'product_id': self.env.ref('product.product_product_4').id,
                        'product_uom_qty': 1,
                        'price_unit': 100,
                    })]
                })

    @api.depends("result_ids.time", "result_ids.event_id.style_id")
    def _compute_best_times(self):
        for s in self:
            lines = []
            styles = self.env['natacio.style'].search([])
            for st in styles:
                best = self.env['natacio.result'].search([
                    ('swimmer_id', '=', s.id),
                    ('event_id.style_id', '=', st.id),
                    ('time', '>', 0)
                ], order='time asc', limit=1)
                if best:
                    lines.append(f"{st.name}: {best.time}s ({best.event_id.name})")
            s.best_times_summary = "\n".join(lines)

    @api.constrains('category_id', 'birth_year')
    def _check_category_age(self):
        for s in self:
            if s.category_id and s.birth_year:
                age = date.today().year - s.birth_year
                if s.category_id.age_min is not None and age < s.category_id.age_min:
                    raise ValidationError(
                        f"El nadador {s.name} té {age} anys, és menor que l'edat mínima de la categoria {s.category_id.name}."
                    )
                if s.category_id.age_max is not None and age > s.category_id.age_max:
                    raise ValidationError(
                        f"El nadador {s.name} té {age} anys, és major que l'edat màxima de la categoria {s.category_id.name}."
                    )

# ===============
# CHAMPIONSHIP
# ================
class Championship(models.Model):
    _name = "natacio.championship"
    _description = "Campionat"

    name = fields.Char(string="Nom", required=True)
    club_ids = fields.Many2many("natacio.club", string="Clubs participants")
    swimmer_ids = fields.Many2many("natacio.swimmer", string="Nadadors inscrits")
    session_ids = fields.One2many("natacio.session", "championship_id", string="Sessions")
    date_start = fields.Date(string="Data inici")
    date_end = fields.Date(string="Data final")
    ranking = fields.Text(string="Classificació general", compute="_compute_ranking", store=True)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError("La data d'inici ha de ser anterior a la data final.")

    @api.constrains('swimmer_ids', 'club_ids')
    def _check_swimmers_in_clubs(self):
        for rec in self:
            club_ids = rec.club_ids.ids
            for swimmer in rec.swimmer_ids:
                if swimmer.club_id and swimmer.club_id.id not in club_ids:
                    raise ValidationError(
                        f"El nadador {swimmer.name} no pertany a cap club inscrit en el campionat."
                    )

    @api.depends('swimmer_ids.result_ids.points')
    def _compute_ranking(self):
        for champ in self:
            ranking = {}
            for swimmer in champ.swimmer_ids:
                ranking[swimmer] = sum(r.points for r in swimmer.result_ids)
            ordered = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
            
            champ.ranking = "\n".join(f"{i+1}. {s.name} - {pts} punts" for i, (s, pts) in enumerate(ordered))


# ============
# SESSION
# ============
class Session(models.Model):
    _name = "natacio.session"
    _description = "Sessió"

    name = fields.Char(string="Nom de la sessió", required=True)
    championship_id = fields.Many2one("natacio.championship", string="Campionat", ondelete='cascade')
    date = fields.Datetime(string="Data i hora")
    event_ids = fields.One2many("natacio.event", "session_id", string="Proves")

    @api.constrains('date', 'championship_id')
    def _check_session_overlap(self):
        for rec in self:
            if rec.date and rec.championship_id:
                other = self.search([
                    ('id', '!=', rec.id),
                    ('championship_id', '=', rec.championship_id.id),
                    ('date', '=', rec.date)
                ], limit=1)
                if other:
                    raise ValidationError("Ja existeix una sessió amb la mateixa data/hora en aquest campionat.")

# =========
# EVENT
# =========
class Event(models.Model):
    _name = "natacio.event"
    _description = "Prova"

    name = fields.Char(string="Descripció", required=True)
    session_id = fields.Many2one("natacio.session", string="Sessió", ondelete='cascade')
    style_id = fields.Many2one("natacio.style", string="Estil", ondelete='set null')
    category_id = fields.Many2one("natacio.category", string="Categoria", ondelete='set null')
    registrant_ids = fields.Many2many("natacio.swimmer", string="Inscrits")
    series_ids = fields.One2many("natacio.series", "event_id", string="Sèries")
    ranking = fields.Text(string="Ranking", compute="_compute_ranking")

    @api.depends('series_ids.result_ids.points', 'series_ids.result_ids.time')
    def _compute_ranking(self):
        for ev in self:
            results = self.env['natacio.result'].search([('event_id', '=', ev.id)], order='points desc, time asc')
            lines = []
            for i, r in enumerate(results):
                lines.append(f"{i+1}. {r.swimmer_id.name} - {r.points:.2f} pts - {r.time}s")
            ev.ranking = "\n".join(lines)

# =========
# RESULT
# =========
class Result(models.Model):
    _name = "natacio.result"
    _description = "Resultat d'una sèrie"

    swimmer_id = fields.Many2one("natacio.swimmer", string="Nadador", required=True, ondelete='cascade')
    event_id = fields.Many2one("natacio.event", string="Prova", required=True, ondelete='cascade')
    series_id = fields.Many2one("natacio.series", string="Sèrie", ondelete='set null')
    time = fields.Float(string="Temps (s)", required=True)
    points = fields.Float(string="Punts", compute="_compute_points", store=True)

    @api.depends('time')
    def _compute_points(self):
        for r in self:
            r.points = 1000.0 / r.time if r.time and r.time > 0 else 0.0

    @api.constrains('swimmer_id', 'event_id')
    def _check_swimmer_registration(self):
        for r in self:
            swimmer = r.swimmer_id
            event = r.event_id
            if event and swimmer:
                in_registrants = swimmer in event.registrant_ids
                in_series = r.series_id and swimmer in r.series_id.swimmer_ids
                if not in_registrants and not in_series:
                    raise ValidationError(
                        f"El nadador {swimmer.name} no està inscrit a la prova {event.name}."
                    )
                if swimmer.last_payment_date and (date.today() - swimmer.last_payment_date).days > 365:
                    raise ValidationError(f"{swimmer.name} no té quota vigent.")

# ========
# SERIES
# ========
class Series(models.Model):
    _name = "natacio.series"
    _description = "Sèrie d'una prova"

    name = fields.Char(string="Nom de la sèrie", required=True)
    event_id = fields.Many2one("natacio.event", string="Prova", ondelete='cascade')
    swimmer_ids = fields.Many2many("natacio.swimmer", string="Nadadors")
    result_ids = fields.One2many("natacio.result", "series_id", string="Resultats")
