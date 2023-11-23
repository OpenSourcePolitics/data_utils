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
    def __init__(self, display, name, forms_summary, **kwargs):
        self.display = display
        self.name = name
        self.params = {
                'name': self.name,
                'display': self.display,
                'dataset_query': {
                    'database': forms_summary.database_id,
                    'query': {
                        'source-table': f'card__{forms_summary.form_model_id}'
                    },
                    'type': 'query'
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
        filter_params = None
        if self.filters:
            if len(self.filters) == 1:
                filter_params = self.filters[0].to_params()
            else:
                filter_params = ['and']
                for filter in self.filters:
                    filter_params.append(filter.to_params())
            self.params['dataset_query']['query']['filter'] = filter_params

        if self.aggregation:
            aggregation, breakout = self.aggregation.to_params()
            self.params['dataset_query']['query']['aggregation'] = aggregation
            self.params['dataset_query']['query']['breakout'] = breakout

        if self.fields:
            self.params['dataset_query']['query']['fields'] = (
                self.fields.to_params()
            )

        if self.custom_params:
            for custom_param in self.custom_params:
                self.params[custom_param["name"]] = custom_param["value"]

        if self.order:
            self.params['dataset_query']['query']['order_by'] = (
                self.order.to_params()
            )

        chart = MTB.create_card(custom_json=self.params, return_card=True)
        print(f'Chart created : {chart["name"]} with ID {chart["id"]}')
        return chart

    def set_filters(self, filter):
        assert isinstance(filter, Filter)
        self.filters.append(filter)

    def set_aggregation(self, aggregation):
        assert isinstance(aggregation, Aggregation)
        self.aggregation = aggregation

    def set_fields(self, fields):
        assert isinstance(fields, Fields)
        self.fields = fields

    def set_order(self, order):
        assert isinstance(order, Order)
        self.order = order

    def set_custom_params(self, kwargs_list):
        self.custom_params = kwargs_list


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
