from floriday_magic_wand.web import render_index_html


def test_render_index_has_tabs() -> None:
    html = render_index_html()
    assert "Upload & Vrijstaand" in html
    assert "Beeldbank" in html
    assert "/api/media" in html
