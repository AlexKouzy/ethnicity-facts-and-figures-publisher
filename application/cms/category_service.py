import logging

from application import db

from application.cms.models import (
    Page,
    Dimension,
    Category,
    CategoryValue,
    DimensionCategory)

from application.utils import setup_module_logging

logger = logging.Logger(__name__)

'''
The category service is in charge of all CRUD for categories and values

Categories
CategoryValues
&
DimensionCategories

which chain together in many-to-many relationships

'''


class CategoryService:

    def __init__(self):
        self.logger = logger

    def init_app(self, app):
        self.logger = setup_module_logging(self.logger, app.config['LOG_LEVEL'])
        self.logger.info('Initialised category service')

    '''
    CATEGORY Management
    '''

    def create_category(self, family, subfamily, title, position=999):
        category = Category(title=title, family=family, subfamily=subfamily, position=position)
        db.session.add(category)
        db.session.commit()
        return category

    def delete_category(self, category_id):
        category = self.get_category_by_id(category_id)
        if DimensionCategory.query.filter_by(category_id=category_id).count() == 0:
            self._remove_category_values(category)
        db.session.delete(category)
        db.session.commit()

    def get_category(self, family, title):
        return Category.query.filter_by(title=title, family=family).first()

    def get_category_by_id(self, category_id):
        return Category.query.filter_by(id=category_id).first()

    def get_all_categories(self):
        categories = Category.query.all()
        return categories

    def get_categories_by_family(self, family):
        categories = Category.query.filter_by(family=family)

        # get a list of unique subfamilies
        subfamilies = list(set([category.subfamily for category in categories]))
        subfamilies.sort()

        # get a list of categories for each subfamily
        results = []
        for subfamily in subfamilies:
            results = results + [{
                'subfamily': subfamily,
                'categories': Category.query.filter_by(family=family, subfamily=subfamily).order_by(Category.position)
            }]
        return results

    def edit_category(self, family, title, family_update, subfamily_update, title_update, position_update):
        category = self.get_category(family, title)
        category.family = family_update
        category.subfamily = subfamily_update
        category.title = title_update
        category.position = position_update
        db.session.add(category)
        db.session.commit()

    '''
    CATEGORY >-< DIMENSION relationship management
    '''

    def link_category_to_dimension(self, dimension, family, category_title,
                                   includes_parents, includes_all, includes_unknown):
        dimension_guid = dimension.guid
        category = self.get_category(family=family, title=category_title)
        category_id = category.id

        db_dimension_category = DimensionCategory(dimension_guid=dimension_guid,
                                                  category_id=category_id,
                                                  includes_parents=includes_parents,
                                                  includes_all=includes_all,
                                                  includes_unknown=includes_unknown)

        dimension.category_links.append(db_dimension_category)
        db.session.add(dimension)
        category.dimension_links.append(db_dimension_category)
        db.session.add(category)
        db.session.commit()
        return db_dimension_category

    def unlink_category_from_dimension(self, dimension, family, category_title):
        category = self.get_category(family=family, title=category_title)

        link = DimensionCategory.query.filter_by(category_id=category.id, dimension_guid=dimension.guid).first()

        db.session.delete(link)
        db.session.commit()

    def get_category_for_dimension(self, dimension, family):
        for link in dimension.category_links:
            if link.category.family == family:
                return link
        return None

    def unlink_dimension_from_family(self, dimension, family):
        for link in dimension.category_links:
            if link.category.family == family:
                db.session.delete(link)
        db.session.commit()

    '''
    VALUE management
    '''

    def get_value(self, value):
        return CategoryValue.query.filter_by(value=value).first()

    def get_all_values(self):
        values = CategoryValue.query.all()
        return [v.value for v in values]

    def create_category_value(self, value_string):
        category_value = self.get_value(value=value_string)
        if category_value:
            return category_value
        else:
            category_value = CategoryValue(value=value_string)
            db.session.add(category_value)
            db.session.commit()
            return category_value

    def create_or_get_category_value(self, value_string):
        category_value = self.get_value(value=value_string)
        if category_value:
            return category_value
        else:
            return self.create_category_value(value_string=value_string)

    def clean_value_database(self):
        values = CategoryValue.query.all()
        for value in values:
            if len(value.categories) == 0:
                db.session.delete(value)
                db.session.commit()

    '''
    CATEGORY >-< VALUE relationship management
    '''

    def add_category_value_to_category(self, category_family, category_title, value_title):
        category = self.get_category(title=category_title, family=category_family)
        value = self.get_value(value=value_title)
        category.values.append(value)

        db.session.add(category)
        db.session.commit()
        return category

    def remove_value_from_category(self, family, category_title, value_string):
        category = self.get_category(family=family, title=category_title)
        value = self.get_value(value=value_string)

        category.values.remove(value)
        db.session.add(category)
        db.session.commit()

    def _remove_category_values(self, category):
        for value in category.values:
            db.session.delete(value)
        db.session.commit()


category_service = CategoryService()
