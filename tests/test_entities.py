from src.entities import Team, Fixture


def test_fixture_post_init(fixture: Fixture):
    # given - when - then
    assert fixture.is_next_day == ""
    assert fixture.futbol_libre_url == "https://futbollibre.net"
    assert fixture.futbol_para_todos_url == "https://futbolparatodos.online/es/"
    assert fixture.line_up == None
    assert fixture.highlights == [f"https://www.youtube.com/results?search_query=River Plate+vs+Boca Juniors+jugadas+resumen"]
    assert fixture.head_to_head == []


