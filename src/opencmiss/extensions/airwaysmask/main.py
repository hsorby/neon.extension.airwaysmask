import os

from PySide2.QtWidgets import QFileDialog

from opencmiss.neon.extensions.airways import AirwaysMask
from opencmiss.extensions.airwaysmask import __version__ as extension_version
from opencmiss.extensions.airwaysmask.model import ModelAirwaysMask, allowed_axes
from opencmiss.extensions.airwaysmask.scene import SceneAirwaysMask


class MainAirwaysMask(AirwaysMask):
    """
    Main class for the Airways Neon extension.
    """

    def __init__(self, main_view):
        self._empty = ""
        self._main_view = main_view
        self._model = ModelAirwaysMask(main_view.get_zinc_context())
        self._scene = SceneAirwaysMask(self._model)

    def save(self):
        saved_data = {"version": extension_version, "empty": self._empty}

        return saved_data

    def _load_setting(self, json_data, key):
        if key in json_data:
            setattr(self, "_%s" % key, json_data[key])

    def open(self, saved_data):
        if "version" in saved_data:
            if saved_data["version"] in extension_version:
                self._load_setting(saved_data, "empty")

    def import_analyze_data(self):
        # file_name, file_type = QFileDialog.getOpenFileName(self._main_view,
        #                                                    "Import Analyze header",
        #                                                    self._main_view.get_start_directory(),
        #                                                    "Analyze header (*.hdr)")
        file_name = "/Users/hsor001/Projects/opencmiss/builds/opencmiss_libraries/src/zinc/tests/resources/bigendian.hdr"
        # file_name = "/Users/hsor001/Projects/Data/LungGroup/ohio/P2BRP268-H12816.hdr"
        file_type = "Analyze header (*.hdr)"
        if file_name:
            self._main_view.set_start_directory(os.path.dirname(file_name))
            self._model.load_mask(file_name)
            self._scene.set_image_material()

    def apply_scene_filters(self):
        view = self._main_view.get_view('OrthographicPlus')
        view_widget = self._main_view.get_view_widget_at(view.get_index())
        for axis in allowed_axes:
            scene_viewer = view_widget.get_orthographic_view(axis)
            scene_filter = self._scene.get_scene_filter(axis)
            scene_viewer.setScenefilter(scene_filter)

