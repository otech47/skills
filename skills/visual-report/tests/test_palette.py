import colorsys
import importlib.util
from pathlib import Path
import re
import unittest

spec = importlib.util.spec_from_file_location("flair", Path(__file__).resolve().parents[1] / "scripts/roll-flair.py")
flair = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flair)


def luminance(rgb):
    values = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return sum(c * w for c, w in zip(values, (0.2126, 0.7152, 0.0722)))


def hsl(value):
    hue, saturation, lightness = map(float, re.findall(r"[0-9.]+", value))
    return colorsys.hls_to_rgb(hue / 360, lightness / 100, saturation / 100)


class PaletteTests(unittest.TestCase):
    def test_text_accent_contrast_on_all_report_surfaces(self):
        backgrounds = {"light": [(251, 251, 250), (255, 255, 255), (244, 244, 242)], "dark": [(22, 22, 26), (30, 30, 36), (38, 38, 46)]}
        for _ in range(200):
            for theme, (accent, soft, _) in flair.roll_colors().items():
                surfaces = [tuple(c / 255 for c in bg) for bg in backgrounds[theme]] + [hsl(soft)]
                for surface in surfaces:
                    a, b = sorted([luminance(hsl(accent)), luminance(surface)])
                    self.assertGreaterEqual((b + 0.05) / (a + 0.05), 4.5, (theme, accent, soft))


if __name__ == "__main__":
    unittest.main()
