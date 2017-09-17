import unittest
from object_detector_app.utils.app_utils import color_name_to_rgb, standard_colors


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.colors = color_name_to_rgb()
        self.standard_colors = standard_colors()

    def test_all_colors(self):
        """Test that manual defined colors are also in the matplotlib color name space."""
        color_list = set(sorted(list(self.colors.keys())))
        standard_color_list = set(sorted([color.lower() for color in self.standard_colors]))
        color_common = standard_color_list.intersection(color_list)
        self.assertEqual(len(color_common), len(standard_color_list))
