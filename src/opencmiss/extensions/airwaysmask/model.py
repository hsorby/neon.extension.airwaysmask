from opencmiss.utils.zinc import createFiniteElementField, createCubeFiniteElement
from opencmiss.zinc.field import FieldImage
from opencmiss.zinc.status import OK as STATUS_OK

from opencmiss.extensions.airwaysmask.utils import generate_offset_cube_coordinates

allowed_axes = ['x', 'y', 'z']


class ModelAirwaysMask(object):

    def __init__(self, zinc_context):
        self._zinc_context = zinc_context
        self._region = zinc_context.getDefaultRegion()
        materials_module = self._zinc_context.getMaterialmodule()

        self._coordinate_field = None
        self._image_field = None
        self._image_material = None

        self._x_material = materials_module.findMaterialByName('red')
        self._x_value_field = None
        self._x_fixed_component_field = None
        self._x_normal_field = None
        self._x_coordinate_contour_field = None

        self._y_material = materials_module.findMaterialByName('green')
        self._y_value_field = None
        self._y_fixed_component_field = None
        self._y_normal_field = None
        self._y_coordinate_contour_field = None

        self._z_material = materials_module.findMaterialByName('blue')
        self._z_value_field = None
        self._z_fixed_component_field = None
        self._z_normal_field = None
        self._z_coordinate_contour_field = None

        self._setup_region()

    def get_zinc_context(self):
        return self._zinc_context

    def get_region(self):
        return self._region

    def get_image_material(self):
        return self._image_material

    def set_plane_value(self, axis, value):
        """
        Set the value of the given axis into the correct iso scalar field, axis should be one of: ['x', 'y', 'z'].
        :param axis: One of 'x', 'y', or 'z'.
        :param value: The value to set.
        """
        if axis in allowed_axes:
            attribute = getattr(self, '_%s_value_field' % axis)
            field_cache = attribute.getFieldmodule().getFieldcache()
            attribute.assignReal(field_cache, value)

    def get_contour_field(self, axis):
        return getattr(self, '_%s_coordinate_contour_field' % axis)

    def get_plane_field(self, axis):
        return getattr(self, '_%s_fixed_component_field' % axis)

    def get_material(self, axis):
        return getattr(self, '_%s_material' % axis)

    def load_mask(self, file_name):
        field_module = self._region.getFieldmodule()
        image_field = field_module.createFieldImage()
        image_field.setName('mask')
        stream_information = image_field.createStreaminformationImage()
        stream_information.setFileFormat(stream_information.FILE_FORMAT_ANALYZE)
        stream_information.createStreamresourceFile(file_name)
        result = image_field.read(stream_information)
        if result == STATUS_OK:
            image_field.setWrapMode(FieldImage.WRAP_MODE_BORDER_CLAMP)
            image_field.setFilterMode(FieldImage.FILTER_MODE_NEAREST)
            print('Analyze data loaded successfully.')
            print(image_field.getWidthInPixels(), image_field.getHeightInPixels(), image_field.getDepthInPixels())
            # print(image_field.getProperty("bob"))
            # –32,768 to 32,767
            constant_field_1 = field_module.createFieldConstant(-32000)
            constant_field_2 = field_module.createFieldConstant(30)
            field_1 = field_module.createFieldSubtract(image_field, constant_field_1)
            field_2 = field_module.createFieldMultiply(field_1, constant_field_2)
            adjusted_image_field = field_module.createFieldImageFromSource(field_2)
            self._image_field = image_field
            self._update_cube_dimensions()
            self._create_image_field_material()
        else:
            self._image_field = None
            print('Error: Failed to load mask.')

    def _setup_region(self):
        self._coordinate_field = createFiniteElementField(self._region)
        node_coordinates = generate_offset_cube_coordinates([1, 1, 1])
        field_module = self._region.getFieldmodule()
        createCubeFiniteElement(field_module, self._coordinate_field, node_coordinates)
        zero_field = field_module.createFieldConstant(0.0)
        x_component_field = field_module.createFieldComponent(self._coordinate_field, 1)
        y_component_field = field_module.createFieldComponent(self._coordinate_field, 2)
        z_component_field = field_module.createFieldComponent(self._coordinate_field, 3)

        self._x_value_field = field_module.createFieldConstant(2.0)
        self._x_fixed_component_field = field_module.createFieldConcatenate([self._x_value_field,
                                                                             y_component_field,
                                                                             z_component_field])
        self._x_fixed_component_field.setName('fixed_x_coordinates')
        x_point_on_plane_field = field_module.createFieldConcatenate(
            [self._x_value_field, zero_field, zero_field])
        self._x_normal_field = field_module.createFieldConstant([1, 0, 0])
        self._x_coordinate_contour_field = _create_iso_scalar_field(field_module, self._coordinate_field,
                                                                    self._x_normal_field, x_point_on_plane_field)
        self._y_value_field = field_module.createFieldConstant(5.0)
        self._y_fixed_component_field = field_module.createFieldConcatenate([x_component_field,
                                                                             self._y_value_field,
                                                                             z_component_field])
        self._y_fixed_component_field.setName('fixed_y_coordinates')
        y_point_on_plane_field = field_module.createFieldConcatenate(
            [zero_field, self._y_value_field, zero_field])
        self._y_normal_field = field_module.createFieldConstant([0, 1, 0])
        self._y_coordinate_contour_field = _create_iso_scalar_field(field_module, self._coordinate_field,
                                                                    self._y_normal_field, y_point_on_plane_field)
        self._z_value_field = field_module.createFieldConstant(3.0)
        self._z_fixed_component_field = field_module.createFieldConcatenate([x_component_field,
                                                                             y_component_field,
                                                                             self._z_value_field])
        self._z_fixed_component_field.setName('fixed_z_coordinates')
        z_point_on_plane_field = field_module.createFieldConcatenate(
            [zero_field, zero_field, self._z_value_field])
        self._z_normal_field = field_module.createFieldConstant([0, 0, 1])
        self._z_coordinate_contour_field = _create_iso_scalar_field(field_module, self._coordinate_field,
                                                                    self._z_normal_field, z_point_on_plane_field)

    def _update_cube_dimensions(self):
        result, dimensions = self._image_field.getSizeInPixels(3)
        if result != 3:
            print("Something has gone wrong????", result)

        cube_node_coordinates = generate_offset_cube_coordinates(dimensions)
        field_module = self._image_field.getFieldmodule()
        field_cache = field_module.createFieldcache()
        node_set = field_module.findNodesetByName('nodes')
        for i, node_coordinates in enumerate(cube_node_coordinates):
            node = node_set.findNodeByIdentifier(i + 1)
            field_cache.setNode(node)
            self._coordinate_field.assignReal(field_cache, node_coordinates)

    def _create_image_field_material(self):
        """
        Use an image field in a material to create an OpenGL texture.  Stores the
        created material in _image_material.
        """
        # create a graphics material from the graphics module, assign it a name
        # and set flag to true
        materials_module = self._zinc_context.getMaterialmodule()
        material = materials_module.createMaterial()


        # spectrum_module = self._zinc_context.getSpectrummodule()
        # spectrum = spectrum_module.createSpectrum()
        # component = spectrum.createSpectrumcomponent()
        # component.setColourMappingType(component.COLOUR_MAPPING_TYPE_MONOCHROME)
        # component.setRangeMinimum(0)
        # component.setRangeMaximum(1)

        # material.setSpectrum(spectrum)

#         fieldmodule = image_field.getFieldmodule()
#         histogram_field = fieldmodule.createFieldImagefilterHistogram(image_field)
#         print histogram_field.getMarginalScale()
#         print histogram_field.getNumberOfBins(10)
#         print histogram_field.getComputeMinimumValues(10)
#         print histogram_field.getComputeMaximumValues(10)
#         rescaled_image_field = fieldmodule.createFieldImagefilterRescaleIntensity(image_field, 0, 1)
#         actual_rescaled_image_field = fieldmodule.createFieldImageFromSource(rescaled_image_field)
        # Create an image field. A temporary xi source field is created for us.
        material.setTextureField(1, self._image_field)

        self._image_material = material

def _create_iso_scalar_field(field_module, finite_element_field, plane_normal_field, point_on_plane_field):
    d = field_module.createFieldDotProduct(plane_normal_field, point_on_plane_field)
    iso_scalar_field = field_module.createFieldDotProduct(finite_element_field, plane_normal_field) - d

    return iso_scalar_field
