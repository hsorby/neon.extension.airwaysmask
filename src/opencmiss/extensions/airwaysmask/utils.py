

def generate_offset_cube_coordinates(dimensions):
    """
    Create a set of eight 3D coordinates that are offset by 0.5.  In this case the 0.5 is a pixel so that
    the centre of the voxel is at the integer coordinate location.

    :param dimensions: A list of size three containing the dimensions of the cube.
    :return: A list of 3D coordinates for the offset cube.
    """
    node_coordinate_set = [[0 - 0.5, 0 - 0.5, 0 - 0.5],
                           [dimensions[0] + 0.5, 0 - 0.5, 0 - 0.5],
                           [0 - 0.5, dimensions[1] + 0.5, 0 - 0.5],
                           [dimensions[0] + 0.5, dimensions[1] + 0.5, 0 - 0.5],
                           [0 - 0.5, 0 - 0.5, dimensions[2] + 0.5],
                           [dimensions[0] + 0.5, 0 - 0.5, dimensions[2] + 0.5],
                           [0 - 0.5, dimensions[1] + 0.5, dimensions[2] + 0.5],
                           [dimensions[0] + 0.5, dimensions[1] + 0.5, dimensions[2] + 0.5]]
    return node_coordinate_set
