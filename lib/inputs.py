import time
import math

import utils as utils
import models as m
from app import app, settings, db, excel_files


def get_sites(benchmark_id):
    items = []
    sites = m.Site.query.filter_by(benchmark_id=benchmark_id).all()
    site_ids = [s.id for s in sites]

    for item in sites:
        items.append({
            'class': "grey lighten-3" if not item.active else '',
            'id': item.id,
            'name': item.name,
            'country': item.country,
            # 'active': item.active,
            'employees': item.employees,
            'goal_statuses': [
                {'name': 'BE01', },
                {'name': 'BE02', },
                {'name': 'BE05', },
                {'name': 'BE06', },
                {'name': 'BE07', },
                {'name': 'BE08', },
                {'name': 'BE09', },
            ],
        })

    return {
        'items': items,
        'name': 'Sites',
        'name_singular': 'Site',
        'url': 'sites',
        'headers':  [
            {'text': 'Name', 'value': 'name', 'align': 'start', },
            {'text': 'Country', 'value': 'country', },
            {'text': 'Employees', 'value': 'employees', },
            {'text': 'Linked Goals', 'value': 'status', },
            {'text': 'Actions', 'value': 'actions', 'sortable': False},
        ],
    }


def get_purchases(benchmark_id):
    items = []
    purchases = m.Purchase.query.filter_by(benchmark_id=benchmark_id).all()

    for item in purchases:
        items.append({
            'id': item.id,
            'name': item.name,
            'type': item.type,
            'cost': item.cost,
            'traceable': item.traceable,
            'status': item.status,
        })

    return {
        'items': items,
        'name': 'Purchases',
        'name_singular': 'Purchase',
        'url': 'purchases',
        'headers':  [
            {'text': 'Name', 'value': 'name', 'align': 'start', },
            {'text': 'Type', 'value': 'type', },
            {'text': 'Cost', 'value': 'cost', },
            {'text': 'Is Traceable', 'value': 'traceable', },
            {'text': 'Status', 'value': 'status', },
            {'text': 'Actions', 'value': 'actions', 'sortable': False},
        ],
    }


def get_natural_resources(benchmark_id):
    items = []
    purchases = m.NaturalResource.query.filter_by(benchmark_id=benchmark_id).all()

    for item in purchases:
        items.append({
            'id': item.id,
            'type': item.type,
            'name': item.name,
            'status': item.status,
            'value': item.value,
            'country': item.country,
        })

    return {
        'items': items,
        'name': 'Natual Resources',
        'name_singular': 'Natual Resource',
        'url': 'natural_resources',
        'headers':   [
            {'text': 'Name', 'value': 'name', 'align': 'start', },
            {'text': 'Type', 'value': 'type', },
            {'text': 'Country', 'value': 'country', },
            {'text': 'Value', 'value': 'value', },
            {'text': 'Status', 'value': 'status', },
            {'text': 'Actions', 'value': 'actions', 'sortable': False},
        ],
    }
