"""One module per new certificate lesson. Each module's build() returns one lesson.

Modules are listed in recommended order; course membership comes from the lesson id prefix and
tools/certification_course/blueprint.py. Lessons never share identities across the two courses.
"""
MODULES = [
    'aice_python_tools', 'aice_data_types', 'aice_row_conditions',
    'aice_data_summary', 'aice_visualization', 'aice_data_quality',
    'aice_target_features', 'aice_data_split', 'aice_encoding', 'aice_scaling',
    'aice_regression', 'aice_classification', 'aice_model_improvement',
    'engineer_java_first', 'engineer_control_first', 'engineer_java_objects',
]

# A published revision never changes. When a lesson's bytes change after publishing (its text or
# the shared checker), give it the next revision here; the build refuses a changed pinned revision.
REVISIONS = {
    # v1.0.1: the shared Python checker learned array comparison and hides library warnings.
    'aice-python-tools': 'v1.0.1',
    'aice-data-types': 'v1.0.1',
    'aice-row-conditions': 'v1.0.1',
    # v1.0.1: two statements now also hold on the exam's pandas 1.5.3, which drops text columns instead of raising.
    'aice-data-summary': 'v1.0.1',
}
