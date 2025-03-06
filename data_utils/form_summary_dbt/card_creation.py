from ..utils import MTB


class Filter:
    def __init__(self, filter_type, field, value, field_type='type/Text'):
        self.type = filter_type
        self.field = field
        self.value = value
        self.field_type = field_type

    def to_params(self):
        return [
            self.type,
            [
                'field',
                self.field,
                {'base-type': self.field_type}
            ],
            self.value
        ]


class Aggregation:
    def __init__(self, aggregation_type, fields):
        self.type = aggregation_type
        self.fields = fields

    def to_params(self):
        if self.type[0] == 'count':
            aggregation = [[self.type][0]]
        # TODO : improve aggregation
        elif self.type[0] == 'sum':
            aggregation_type = 'sum'
            aggregation_field = self.type[1]
            aggregation = aggregation_field.to_params()
            aggregation.insert(0, aggregation_type)
        breakout = self.fields.to_params()
        return aggregation, breakout


class Fields:
    def __init__(self, field_list):
        self.field_list = field_list

    def to_params(self):
        params = []
        for field in self.field_list:
            params.append([
                "field", field["name"], {"base-type": field["type"]}
            ])
        return params


class Order:
    def __init__(self, order_direction='asc', criteria=None):
        self.order_direction = order_direction
        # TODO
        self.criteria = criteria

    def to_params(self):
        params = []
        params.append([
            self.order_direction,
            ["aggregation", 0, None]
        ])
        return params


class Chart:
    def __init__(self, display, name, forms_summary, query=None):
        self.display = display
        self.name = name
        self.query = query
        self.params = {
            'name': self.name,
            'display': self.display,
            'dataset_query': {
                'database': forms_summary.database_id,
                'native': {
                    'query': self.query
                },
                'type': 'native'
            },
            'collection_id': forms_summary.collection_id
        }
        self.filters = []
        self.aggregation = None
        self.fields = None
        self.order = None
        self.custom_params = None
        self.row = 0
        self.col = 0
        self.size_x = 4
        self.size_y = 4


    def create_chart(self):
        chart = MTB.create_card(custom_json=self.params, return_card=True)
        print(f'Chart created: {chart["name"]} with ID {chart["id"]}')
        return chart


class PieChart(Chart):
    def __init__(self, *args, **kwargs):
        super().__init__('pie', *args, **kwargs)
        self.size_x = 6


class TableChart(Chart):
    def __init__(self, *args, **kwargs):
        super().__init__('table', *args, **kwargs)
        self.size_x = 18


class BarChart(Chart):
    def __init__(self, *args, **kwargs):
        super().__init__('bar', *args, **kwargs)
        self.size_x = 6


class HorizontalBarChart(Chart):
    def __init__(self, *args, **kwargs):
        super().__init__('row', *args, **kwargs)
        self.size_x = 9
