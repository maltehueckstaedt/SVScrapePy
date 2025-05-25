from .helpers import (
    clean_prefixes,
    click_next_page,
    select_semester_and_set_courses
)

from .scrapers import (
    scrape_all_pages,
    scrape_data,
    scrape_inhalte,
    scrape_module,
    scrape_termine,
    scrape_zugeordnete_studiengaenge
)

__all__ = [
    "clean_prefixes",
    "click_next_page",
    "select_semester_and_set_courses",
    "scrape_all_pages",
    "scrape_data",
    "scrape_inhalte",
    "scrape_module",
    "scrape_termine",
    "scrape_zugeordnete_studiengaenge"
]