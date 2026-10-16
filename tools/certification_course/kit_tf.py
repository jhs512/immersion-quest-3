"""TensorFlow exercises: quiet start-up in the checker, otherwise exactly kit.py_task / kit_plots.plot_task.

TensorFlow on Windows logs a GPU notice through Python logging at import. That line is not the
learner's output, so TensorFlow tasks silence the 'tensorflow' logger before the reference or the
learner's code imports it. Only tasks built here carry this, so earlier lessons keep their bytes.
"""
from certification_course import kit
from certification_course.kit_plots import plot_task

ANCHOR = "os.environ['MPLBACKEND'] = 'Agg'\n"
QUIET = (ANCHOR + "os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'\nos.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'\n"
         "import logging\nlogging.getLogger('tensorflow').setLevel(logging.ERROR)\n")


def quiet_tensorflow(t):
    assert t['checker'].count(ANCHOR) == 1, 'kit checker layout changed'
    t['checker'] = t['checker'].replace(ANCHOR, QUIET, 1)
    return t


def tf_task(*args, **kwargs):
    """kit.py_task for code that imports TensorFlow."""
    return quiet_tensorflow(kit.py_task(*args, **kwargs))


def tf_plot_task(*args, **kwargs):
    """kit_plots.plot_task (learning curves) for code that imports TensorFlow."""
    return quiet_tensorflow(plot_task(*args, **kwargs))
