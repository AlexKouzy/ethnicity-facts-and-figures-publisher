import pytest

from tests.functional.data_sets import (
    inject_data,
    simple_data,
    ethnicity_by_time_data,
    ethnicity_by_gender_data,
    granular_data,
    granular_with_parent_data,
)
from tests.functional.pages import (
    LogInPage,
    HomePage,
    TopicPage,
    MeasureEditPage,
    MeasureCreatePage,
    DimensionAddPage,
    DimensionEditPage,
    TableBuilderPage,
    MinimalRandomMeasure,
    MinimalRandomDimension,
)
from tests.functional.utils import spaceless, go_to_page, assert_page_contains, create_measure, login, shuffle_table

pytestmark = pytest.mark.usefixtures("app", "db_session", "stub_measure_page")


def test_can_build_tables(
    driver, app, test_app_editor, live_server, stub_topic_page, stub_subtopic_page, stub_published_measure_page
):
    page = MinimalRandomMeasure()

    table_builder_page = construct_test_table_builder_page(
        driver, live_server, page, stub_subtopic_page, stub_topic_page, test_app_editor, stub_published_measure_page
    )

    run_simple_table_scenarios(table_builder_page, driver)

    run_complex_table_scenarios(table_builder_page, driver)

    run_save_and_load_scenario(table_builder_page, driver)


def construct_test_table_builder_page(
    driver, live_server, page, stub_subtopic_page, stub_topic_page, test_app_editor, stub_published_measure_page
):
    login(driver, live_server, test_app_editor)
    """
    BROWSE TO POINT WHERE WE CAN ADD A MEASURE
    """
    home_page = HomePage(driver, live_server)
    home_page.click_topic_link(stub_topic_page)
    topic_page = TopicPage(driver, live_server, stub_topic_page)
    topic_page.expand_accordion_for_subtopic(stub_subtopic_page)
    """
    SET UP A SIMPLE DIMENSION WE CAN BUILD TEST TABLES ON
    """
    topic_page.click_add_measure(stub_subtopic_page)
    topic_page.wait_until_url_contains("/measure/new")
    create_measure(driver, live_server, page, stub_topic_page, stub_subtopic_page)
    topic_page.wait_until_url_contains("/edit")
    edit_measure_page = MeasureEditPage(driver)
    edit_measure_page.get()
    dimension = MinimalRandomDimension()
    edit_measure_page.click_add_dimension()
    edit_measure_page.wait_until_url_contains("/dimension/new")
    create_dimension_page = DimensionAddPage(driver)
    create_dimension_page.set_title(dimension.title)
    create_dimension_page.set_time_period(dimension.time_period)
    create_dimension_page.set_summary(dimension.summary)
    create_dimension_page.click_save()
    edit_dimension_page = DimensionEditPage(driver)
    edit_dimension_page.get()
    edit_dimension_page.wait_for_seconds(1)
    edit_dimension_page.click_create_table()
    edit_dimension_page.wait_until_url_contains("create_table")
    table_builder_page = TableBuilderPage(driver)
    return table_builder_page


def run_save_and_load_scenario(table_builder_page, driver):
    """
    Check that settings are retained on save
    """
    table_builder_page.refresh()

    """
    GIVEN we build a basic table
    """
    inject_data(driver, simple_data)
    table_builder_page.click_data_okay()
    table_builder_page.wait_for_seconds(1)
    table_builder_page.click_data_edit()
    table_builder_page.wait_for_seconds(1)
    table_builder_page.click_data_cancel()
    table_builder_page.wait_for_seconds(1)

    """
    THEN the edit screen should setup with default preset (for simple data)
    """
    assert table_builder_page.get_ethnicity_settings_code() == "5B"
    assert table_builder_page.get_ethnicity_settings_value() == "ONS 2011 - 5+1"

    """
    WHEN we choose a column to display
    """
    table_builder_page.select_column(1, "Value")
    table_builder_page.wait_for_seconds(1)

    """
    AND we select an alternate preset and save
    """
    table_builder_page.select_ethnicity_settings_value("ONS 2001 - 5+1")

    assert table_builder_page.get_ethnicity_settings_code() == "5A"
    assert table_builder_page.get_ethnicity_settings_value() == "ONS 2001 - 5+1"

    table_builder_page.click_save()
    table_builder_page.wait_for_seconds(1)

    """
    THEN it should reload with the alternate settings
    """
    assert table_builder_page.get_ethnicity_settings_code() == "5A"
    assert table_builder_page.get_ethnicity_settings_value() == "ONS 2001 - 5+1"


def run_simple_table_scenarios(table_builder_page, driver):
    """
    SCENARIO 1. CREATE A SIMPLE TABLE
    """

    """
    GIVEN some basic data appropriate for building simple tables
    """
    inject_data(driver, simple_data)
    table_builder_page.click_data_okay()
    table_builder_page.wait_for_seconds(1)

    """
    THEN the edit screen should get set up
    """
    assert table_builder_page.source_contains("5 rows by 2 columns")
    assert len(table_builder_page.get_ethnicity_settings_list()) == 3
    assert table_builder_page.get_ethnicity_settings_value() == "ONS 2011 - 5+1"

    """
    THEN we select the column to display
    """
    table_builder_page.select_column(1, "Value")
    table_builder_page.wait_for_seconds(1)

    """
    THEN we should have a table with appropriate headers
    """
    assert table_builder_page.table_headers() == ["Ethnicity", "Value"]

    """
    AND we should have a table with appropriate column values
    """
    assert table_builder_page.table_column_contents(1) == ["Asian", "Black", "Mixed", "White", "Other"]
    assert table_builder_page.table_column_contents(2) == ["5", "4", "3", "2", "1"]

    """
    WHEN we select an alternative ethnicity set up
    """
    table_builder_page.select_ethnicity_settings_value("ONS 2001 - 5+1")
    table_builder_page.wait_for_seconds(1)

    """
    THEN the ethnicities that appear in the tables get changed
    """
    assert table_builder_page.table_column_contents(1) == ["Asian", "Black", "Mixed", "White", "Other inc Chinese"]

    """
    SCENARIO 2. CREATE A CHART WITH DISORDERLY DATA
    """

    """
    GIVEN a shuffled version of our simple data
    """
    table_builder_page.refresh()
    inject_data(driver, shuffle_table(simple_data))
    table_builder_page.click_data_okay()

    """
    THEN we select the column to display
    """
    table_builder_page.select_column(1, "Value")
    table_builder_page.wait_for_seconds(1)

    """
    THEN the ethnicities are correctly sorted automatically
    """
    assert table_builder_page.table_column_contents(1) == ["Asian", "Black", "Mixed", "White", "Other"]
    return table_builder_page


def run_complex_table_scenarios(table_builder_page, driver):
    """
    CHART BUILDER CAN BUILD GROUPED BAR TABLES with ethnicity for sub-groups
    """
    """
    GIVEN some basic data appropriate for building grouped bar tables
    """
    table_builder_page.refresh()
    inject_data(driver, ethnicity_by_gender_data)
    table_builder_page.click_data_okay()

    """
    WHEN we set up the complex table options
    """
    table_builder_page.select_data_style("Use ethnicity for rows")
    table_builder_page.wait_for_seconds(1)
    table_builder_page.select_data_style_columns("Gender")
    table_builder_page.select_column(1, "Value")
    table_builder_page.select_column(2, "Gender")
    table_builder_page.wait_for_seconds(1)

    """
    THEN a complex table exists with ethnicities on the left, gender along the top, and sub-columns of value and gender.
    """
    assert table_builder_page.table_headers() == ["Ethnicity", "M", "F"]
    assert table_builder_page.table_secondary_headers() == ["Value", "Gender", "Value", "Gender"]
    assert table_builder_page.table_column_contents(1) == ["Asian", "Black", "Mixed", "White", "Other"]
    assert table_builder_page.table_column_contents(2) == ["5", "4", "3", "2", "1"]
    assert table_builder_page.table_column_contents(3) == ["M"] * 5
    assert table_builder_page.table_column_contents(4) == ["4", "1", "5", "4", "2"]
    assert table_builder_page.table_column_contents(5) == ["F"] * 5