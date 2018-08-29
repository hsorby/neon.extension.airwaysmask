from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.graphics import Graphicslineattributes


class SceneAirwaysMask(object):

    def __init__(self, model):
        self._model = model
        self._x_contour_graphic = None
        self._y_contour_graphic = None
        self._z_contour_graphic = None
        self._create_scene()

    def _create_scene(self):
        region = self._model.get_region()
        field_module = region.getFieldmodule()
        coordinates_field = field_module.findFieldByName('coordinates')

        scene = region.getScene()
        scene.beginChange()
        lines = scene.createGraphicsLines()
        lines.setCoordinateField(coordinates_field)
        lines.setName('cube_outline')

        self._x_contour_graphic = self._create_texture_surface_for_axis(scene, coordinates_field, 'x')
        self._y_contour_graphic = self._create_texture_surface_for_axis(scene, coordinates_field, 'y')
        self._z_contour_graphic = self._create_texture_surface_for_axis(scene, coordinates_field, 'z')

        self._x_plane = self._create_plane_surface_for_axis(scene, 'x')
        self._x_lines = self._create_plane_lines_for_axis(scene, 'x')
        self._y_plane = self._create_plane_surface_for_axis(scene, 'y')
        self._y_lines = self._create_plane_lines_for_axis(scene, 'y')
        self._z_plane = self._create_plane_surface_for_axis(scene, 'z')
        self._z_lines = self._create_plane_lines_for_axis(scene, 'z')
        # _create_node_labels(scene, coordinates_field)
        scene.endChange()

    def _create_texture_surface_for_axis(self, scene, coordinates_field, axis):
        contour_field = self._model.get_contour_field(axis)
        return _create_texture_surface(scene, coordinates_field, contour_field, '%s_contour_graphic' % axis)

    def _create_plane_surface_for_axis(self, scene, axis):
        coordinates = self._model.get_plane_field(axis)
        return _create_surface(scene, coordinates, '%s_surface' % axis)

    def _create_plane_lines_for_axis(self, scene, axis):
        coordinates = self._model.get_plane_field(axis)
        material = self._model.get_material(axis)
        return _create_lines(scene, coordinates, material, '%s_lines' % axis)

    def set_image_material(self):
        image_material = self._model.get_image_material()
        self._x_contour_graphic.setMaterial(image_material)
        self._y_contour_graphic.setMaterial(image_material)
        self._z_contour_graphic.setMaterial(image_material)

    def get_scene_filter(self, axis):
        context = self._model.get_zinc_context()
        scene_filter_module = context.getScenefiltermodule()
        scene_filter_lines = scene_filter_module.createScenefilterGraphicsName('%s_lines' % axis)
        scene_filter_contour = scene_filter_module.createScenefilterGraphicsName('%s_contour_graphic' % axis)
        scene_filter = scene_filter_module.createScenefilterOperatorOr()
        scene_filter.appendOperand(scene_filter_lines)
        scene_filter.appendOperand(scene_filter_contour)

        return  scene_filter


def _create_lines(scene, coordinate_field, material, graphic_name):
    lines = scene.createGraphicsLines()
    lines.setCoordinateField(coordinate_field)
    lines.setMaterial(material)
    lines.setName(graphic_name)
    attributes = lines.getGraphicslineattributes()
    attributes.setShapeType(Graphicslineattributes.SHAPE_TYPE_CIRCLE_EXTRUSION)
    attributes.setBaseSize(0.1)

    return material

def _create_surface(scene, coordinate_field, graphic_name):
    surface = scene.createGraphicsSurfaces()
    surface.setCoordinateField(coordinate_field)
    surface.setName(graphic_name)
    surface.setVisibilityFlag(False)

    return surface

def _create_texture_surface(scene, coordinate_field, iso_scalar_field, graphic_name):

    fm = coordinate_field.getFieldmodule()
    xi = fm.findFieldByName('xi')
    # Create a surface graphic and set it's coordinate field
    # to the finite element coordinate field.
    iso_graphic = scene.createGraphicsContours()
    iso_graphic.setCoordinateField(coordinate_field)
    iso_graphic.setTextureCoordinateField(xi)
    iso_graphic.setIsoscalarField(iso_scalar_field)
    iso_graphic.setListIsovalues(0.0)
    # iso_graphic.setListIsovalues([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
    iso_graphic.setName(graphic_name)

    return iso_graphic

def _create_node_labels(scene, coordinate_field):
    graphic = scene.createGraphicsPoints()
    graphic.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
    graphic.setCoordinateField(coordinate_field)
    graphic.setName('node_coordinate_labels')
    attributes = graphic.getGraphicspointattributes()
    attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_NONE)
    attributes.setLabelField(coordinate_field)
