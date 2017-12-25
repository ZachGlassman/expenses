from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.embed import components
from collections import defaultdict
def generate_type_plot(type_list):
    """excepts a list of tuples (types, cost)"""
    d = defaultdict(int)
    for tup in type_list:
        d[tup[0]] += float(tup[1])

    x = list(sorted(d.keys()))
    y = [d[key] for key in x]
    tot = sum(y)
    y = [i/tot for i in y]
    source = ColumnDataSource(dict(x=x,y=y))
    p = figure(x_range=x)
    p.vbar(source=source, x='x', top='y', width=.5, color='red')
    p.y_range.start = 0
    return components(p)