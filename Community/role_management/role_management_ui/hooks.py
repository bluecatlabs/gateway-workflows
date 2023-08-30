import importlib


def initialize():
    """Handle the `initialize` event."""
    # NOTE: Load the modules that add routes to the blueprint instance.
    # pylint: disable=unused-import
    module_names = [
        "role_management_ui.roleMntPage",
    ]

    for module_name in module_names:
        importlib.import_module(module_name)
