import pytest

from application.cms.page_service import PageService
from tests.functional.pages import LogInPage, IndexPage, CmsIndexPage, TopicPage, SubtopicPage, MeasureEditPage, \
    MeasureCreatePage, RandomMeasure, MeasurePreviewPage

import time

pytestmark = pytest.mark.usefixtures('app', 'db_session', 'stub_measure_page')


def test_can_create_a_measure_page(driver, app,  test_app_editor, live_server,
                                   stub_topic_page, stub_subtopic_page):
    page = RandomMeasure()

    login(driver, live_server, test_app_editor)

    subtopic_page = SubtopicPage(driver, live_server, stub_topic_page, stub_subtopic_page)
    go_to_page(subtopic_page)

    create_measure(driver, live_server, page, stub_subtopic_page, stub_topic_page, subtopic_page)

    edit_measure_page = MeasureEditPage(driver, live_server, stub_topic_page, stub_subtopic_page, page.guid)
    assert edit_measure_page.is_current()

    '''
    Save some information to the edit page
    '''
    edit_measure_page.set_publication_date(page.publication_date)
    edit_measure_page.set_measure_summary(page.measure_summary)
    edit_measure_page.set_main_points(page.main_points)
    edit_measure_page.click_save()
    assert edit_measure_page.is_current()

    '''
    Go to preview page
    '''
    edit_measure_page.click_preview()

    page_service = PageService()
    page_service.init_app(app)
    measure_page = page_service.get_page(page.guid)

    preview_measure_page = MeasurePreviewPage(driver, live_server, stub_topic_page, stub_subtopic_page, measure_page)
    assert preview_measure_page.is_current()

    assert_page_contains(preview_measure_page, page.title)
    assert_page_contains(preview_measure_page, page.measure_summary)
    assert_page_contains(preview_measure_page, page.main_points)


def go_to_page(page):
    page.get()
    assert page.is_current()
    return page


def assert_page_contains(page, text):
    return page.source_contains(text)


def create_measure(driver, live_server, page, stub_subtopic_page, stub_topic_page, subtopic_page):
    subtopic_page.click_new_measure()
    create_measure_page = MeasureCreatePage(driver, live_server, stub_topic_page, stub_subtopic_page)
    create_measure_page.set_guid(page.guid)
    create_measure_page.set_title(page.title)
    create_measure_page.click_save()


def login(driver, live_server, test_app_editor):
    login_page = LogInPage(driver, live_server)
    login_page.get()
    if login_page.is_current():
        login_page.login(test_app_editor.email, test_app_editor.password)