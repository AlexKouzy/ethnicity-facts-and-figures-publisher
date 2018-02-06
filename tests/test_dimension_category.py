import pytest

from datetime import datetime, timedelta

from application.cms.category_service import CategoryService
from application.cms.exceptions import RejectionImpossible
from application.cms.models import Page, Dimension, DimensionCategory, Category, CategoryValue

category_service = CategoryService()


def test_create_category(db_session):
    assert not Category.query.all()

    category = category_service.create_category('Geography', 'Region')

    assert category == Category.query.all()[0]


def test_get_category_returns_category(db_session):

    assert not Category.query.all()

    category_service.create_category('Geography', 'Region 1')
    category_service.create_category('Geography', 'Region 2')
    category_service.create_category('Geography', 'Region 3')
    category_service.create_category('Geography', 'Region 4')
    category_service.create_category('UK Geography', 'Region 2')

    category = category_service.get_category('Geography', 'Region 2')

    assert category is not None
    assert category.title == 'Region 2'
    assert category.family == 'Geography'


def test_get_category_returns_none_for_not_found(db_session):
    assert not Category.query.all()

    category_service.create_category('Geography', 'Region 1')
    category_service.create_category('Geography', 'Region 2')

    category = category_service.get_category('Geography', 'Region 2')
    missing_category = category_service.get_category('Fish', 'Chips')

    assert category is not None
    assert missing_category is None


def test_delete_category_removes_category(db_session):
    # Given some categories
    assert not Category.query.all()
    category_service.create_category('Geography', 'Region 1')
    category_service.create_category('Geography', 'Region 2')
    category_service.create_category('Geography', 'Region 3')
    category_service.create_category('Geography', 'Region 4')

    # When we delete a category
    category = category_service.get_category('Geography', 'Region 3')
    assert category is not None
    category_service.delete_category(category=category)

    # Then it should be deleted
    deleted_category = category_service.get_category('Geography', 'Region 3')
    assert deleted_category is None
    assert Category.query.count() == 3


def test_create_category(db_session):
    assert not Category.query.all()

    category = category_service.create_category('Geography', 'Region')

    assert category == Category.query.all()[0]


def test_get_category_returns_category(db_session):

    assert not Category.query.all()

    category_service.create_category('Geography', 'Region 1')
    category_service.create_category('Geography', 'Region 2')
    category_service.create_category('Geography', 'Region 3')
    category_service.create_category('Geography', 'Region 4')
    category_service.create_category('Geography', 'Region 2')

    category = category_service.get_category('Geography', 'Region 2')

    assert category is not None
    assert category.title == 'Region 2'
    assert category.family == 'Geography'


def test_get_category_returns_none_for_not_found(db_session):
    assert not Category.query.all()

    category_service.create_category('Geography', 'Region 1')
    category_service.create_category('Geography', 'Region 2')

    category = category_service.get_category('Geography', 'Region 2')
    missing_category = category_service.get_category('Fish', 'Chips')

    assert category is not None
    assert missing_category is None


def test_create_value_creates_a_value(db_session):

    assert not CategoryValue.query.all()

    value = category_service.create_or_get_category_value('Camden')

    assert value is not None
    assert value.value == 'Camden'


def test_create_or_get_value_recalls_existing_value(db_session):
    # given a setup with one
    assert not CategoryValue.query.all()
    value = category_service.create_or_get_category_value('Camden')

    # when we recall the value
    value_recalled = category_service.create_or_get_category_value('Camden')

    # then the
    assert value.id == value_recalled.id
    assert CategoryValue.query.count() == 1


def test_add_value_to_category_appends_new_value(db_session):
    # given a setup with one
    category_service.create_category('Geography', 'Greater London Boroughs')
    category_service.create_category('Geography', 'Inner London Boroughs')
    category_service.create_or_get_category_value('Barnet')
    category_service.create_or_get_category_value('Camden')
    category_service.create_or_get_category_value('Haringey')

    # when we add the value
    category_service.add_category_value_to_category('Geography', 'Greater London Boroughs', 'Barnet')
    category_service.add_category_value_to_category('Geography', 'Greater London Boroughs', 'Camden')
    category_service.add_category_value_to_category('Geography', 'Greater London Boroughs', 'Haringey')
    category_service.add_category_value_to_category('Geography', 'Inner London Boroughs', 'Camden')
    category_service.add_category_value_to_category('Geography', 'Inner London Boroughs', 'Haringey')

    # then the
    greater_london = category_service.get_category('Geography', 'Greater London Boroughs')
    inner_london = category_service.get_category('Geography', 'Inner London Boroughs')
    camden = category_service.create_or_get_category_value('Camden')

    assert len(camden.categories) == 2
    assert len(greater_london.values) == 3
    assert len(inner_london.values) == 2


def test_remove_value_from_category_removes_value(db_session):
    # given a setup with one
    category_service.create_category('Geography', 'Greater London Boroughs')
    category_service.create_category('Geography', 'Inner London Boroughs')
    category_service.create_or_get_category_value('Barnet')
    category_service.create_or_get_category_value('Camden')
    category_service.create_or_get_category_value('Haringey')

    category_service.add_category_value_to_category('Geography', 'Greater London Boroughs', 'Barnet')
    category_service.add_category_value_to_category('Geography', 'Greater London Boroughs', 'Camden')
    category_service.add_category_value_to_category('Geography', 'Greater London Boroughs', 'Haringey')
    category_service.add_category_value_to_category('Geography', 'Inner London Boroughs', 'Camden')
    category_service.add_category_value_to_category('Geography', 'Inner London Boroughs', 'Haringey')

    # when we remove the value
    category_service.remove_value_from_category('Geography', 'Inner London Boroughs', 'Camden')

    # then the
    greater_london = category_service.get_category('Geography', 'Greater London Boroughs')
    inner_london = category_service.get_category('Geography', 'Inner London Boroughs')
    camden = category_service.create_or_get_category_value('Camden')

    assert len(camden.categories) == 1
    assert len(greater_london.values) == 3
    assert len(inner_london.values) == 1
    assert 'Inner London Boroughs' not in [c.title for c in camden.categories]
    assert 'Camden' not in [c.value for c in inner_london.values]
    assert 'Camden' in [c.value for c in greater_london.values]
