"""Graph exercises: the learner's figure is compared with the reference figure on every scenario.

plot_task takes the same arguments as kit.py_task. Its checker records each open matplotlib figure
as data — axis labels, title, tick labels, bar rectangles, line points and scatter points — and
compares those records with the reference figure drawn from the same changed data. A picture that
merely looks similar, or one drawn from memorized numbers, does not pass.
"""
from certification_course import kit

SIGNATURE = '''
def figures():
    plt = sys.modules.get('matplotlib.pyplot')
    if plt is None:
        return []
    import numpy as np
    def numbers(values):
        try:
            return [round(float(v), 4) for v in np.asarray(values, dtype=float).ravel()]
        except (TypeError, ValueError):
            return [str(v) for v in values]
    shapes = []
    for number in plt.get_fignums():
        figure = plt.figure(number)
        figure.canvas.draw()
        for ax in figure.axes:
            bars = sorted((round(p.get_x(), 4), round(p.get_width(), 4), round(p.get_y(), 4), round(p.get_height(), 4))
                          for p in ax.patches if type(p).__name__ == 'Rectangle')
            lines = [numbers(line.get_xdata()) + ['|'] + numbers(line.get_ydata()) for line in ax.get_lines()]
            points = []
            for collection in ax.collections:
                offsets = np.asarray(collection.get_offsets())
                if offsets.size:
                    points.append(sorted(tuple(round(float(v), 4) for v in row) for row in offsets.reshape(-1, 2)))
                values = collection.get_array() if hasattr(collection, 'get_array') else None
                if values is not None and getattr(values, 'size', 0):
                    points.append(numbers(values))
            # texts: numbers written on cells, such as a heatmap drawn with annot=True.
            shapes.append(dict(title=ax.get_title(), xlabel=ax.get_xlabel(), ylabel=ax.get_ylabel(),
                xticks=[t.get_text() for t in ax.get_xticklabels()], yticks=[t.get_text() for t in ax.get_yticklabels()],
                bars=bars, lines=sorted(lines, key=str), points=sorted(points, key=str),
                texts=sorted(t.get_text() for t in ax.texts)))
    return shapes
'''

CLOSE = """    plt = sys.modules.get('matplotlib.pyplot')
    if plt is not None:
        plt.close('all')"""


def plot_task(*args, **kwargs):
    """Like kit.py_task, but the drawn figures must match the reference figures too."""
    compare = list(kwargs.pop('compare', ())) + ['__figures__']
    t = kit.py_task(*args, compare=compare, **kwargs)
    checker = t['checker']
    assert checker.count(CLOSE) == 1, 'kit checker layout changed'
    checker = checker.replace(CLOSE, "    scope['__figures__'] = figures()\n" + CLOSE)
    # The kit checker already words a '__figures__' mismatch for learners.
    t['checker'] = checker.replace('\nclass Inputs(', kit.code(SIGNATURE) + '\n\nclass Inputs(', 1)
    return t
