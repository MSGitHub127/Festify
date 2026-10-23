"""Automated accessibility tests ensuring WCAG 2.1 AAA compliance and semantic DOM integrity."""
from __future__ import annotations

import os
import re


def relative_luminance(hex_code: str) -> float:
    """Calculate relative luminance according to WCAG 2.1 definition."""
    hex_code = hex_code.lstrip("#")
    r, g, b = [int(hex_code[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]

    def transform(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r_lin = transform(r)
    g_lin = transform(g)
    b_lin = transform(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculate the contrast ratio between two hex color codes."""
    l1 = relative_luminance(hex1)
    l2 = relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def test_wcag_aaa_contrast_ratios():
    """Verify that every color pair in Festify's palette meets or exceeds WCAG 2.1 AAA (>= 7.0:1)."""
    palette_pairs = [
        ("Primary Body Text (#111827 on #FFFFFF)", "#111827", "#FFFFFF", 7.0),
        ("Secondary Ink (#1F2937 on #FFFFFF)", "#1F2937", "#FFFFFF", 7.0),
        ("Faint Metadata (#374151 on #FFFFFF)", "#374151", "#FFFFFF", 7.0),
        ("Button Accent (#FFFFFF on #1E3A8A)", "#FFFFFF", "#1E3A8A", 7.0),
        ("Canvas Accent (#1E3A8A on #F8F9FA)", "#1E3A8A", "#F8F9FA", 7.0),
        ("Emerald Badge (#044332 on #D1FAE5)", "#044332", "#D1FAE5", 7.0),
        ("Amber Badge (#78350F on #FEF3C7)", "#78350F", "#FEF3C7", 7.0),
        ("Rose Badge (#881337 on #FFE4E6)", "#881337", "#FFE4E6", 7.0),
        ("High Contrast Mode (#000000 on #FFFFFF)", "#000000", "#FFFFFF", 7.0),
    ]

    for label, fg, bg, minimum in palette_pairs:
        ratio = contrast_ratio(fg, bg)
        assert ratio >= minimum, f"Failed WCAG AAA contrast for {label}: got {ratio:.2f}:1, expected >= {minimum}:1"


def test_frontend_index_html_semantic_landmarks():
    """Verify index.html includes essential landmarks, skip link, and live regions."""
    index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
    assert os.path.exists(index_path), f"frontend/index.html not found at {index_path}"

    with open(index_path, encoding="utf-8") as f:
        html = f.read()

    # 1. Skip Navigation Link
    assert '<a class="skip-link" href="#main">Skip to main content</a>' in html

    # 2. Semantic Landmarks
    assert "<header" in html and "</header>" in html
    assert '<main id="main"' in html and "</main>" in html
    assert "<footer" in html and "</footer>" in html

    # 3. Live Region for Screen Readers
    assert 'aria-live="polite"' in html
    assert 'role="status"' in html

    # 4. Tab Navigation ARIA roles
    assert 'role="tablist"' in html
    assert 'role="tab"' in html
    assert 'role="tabpanel"' in html
    assert 'aria-selected=' in html


def test_form_inputs_have_associated_labels():
    """Verify that every input and select in frontend/index.html has a corresponding <label for='...'>."""
    index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
    with open(index_path, encoding="utf-8") as f:
        html = f.read()

    input_ids = re.findall(r'<(?:input|select)\s+[^>]*id="([^"]+)"', html)
    label_fors = re.findall(r'<label\s+[^>]*for="([^"]+)"', html)

    # Any interactive input in the form must have a label
    form_inputs = [i for i in input_ids if i not in ("askInput",)]
    for input_id in form_inputs:
        assert input_id in label_fors, f"Input with id '{input_id}' is missing a corresponding <label for='{input_id}'>"


def test_accessibility_documentation_exists():
    """Verify that ACCESSIBILITY.md is comprehensive and documented."""
    doc_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ACCESSIBILITY.md")
    assert os.path.exists(doc_path), "ACCESSIBILITY.md is missing from repository root"

    with open(doc_path, encoding="utf-8") as f:
        content = f.read()

    assert "WCAG 2.1" in content
    assert "Contrast Ratio Matrix" in content
    assert "Keyboard Navigation" in content
    assert "Web Speech API" in content
