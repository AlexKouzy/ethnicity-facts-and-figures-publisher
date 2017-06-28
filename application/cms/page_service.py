import json
import tempfile
import logging

from datetime import date
from slugify import slugify
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import secure_filename

from application.cms.exceptions import (
    PageUnEditable,
    PageNotFoundException,
    DimensionAlreadyExists,
    DimensionNotFoundException,
    PageExistsException)

from application.cms.models import (
    Dimension,
    DbPage,
    publish_status,
    DbDimension)

from application import db
from application.cms.file_service import file_service
from application.utils import setup_module_logging

logger = logging.Logger(__name__)


class PageService:
    def __init__(self):
        self.logger = logger

    def init_app(self, app):
        self.logger = setup_module_logging(self.logger, app.config['LOG_LEVEL'])
        self.logger.info('Initialised page service')

    def create_page(self, page_type, parent=None, data=None, user=None):
        # TODO: Check page_type is valid
        # TODO: Make default parent homepage
        title = data['title']
        guid = data.pop('guid')
        publication_date = data.pop('publication_date')

        # TODO check db for guid and uri, should be unique
        try:
            page_service.get_page(guid)
        except PageNotFoundException as e:
            self.logger.exception('Page with guid %s does not exist ok to proceed', guid)
        else:
            raise PageExistsException()

        db_page = DbPage(guid=guid, uri=slugify(title),
                         parent_guid=parent,
                         page_type=page_type,
                         page_json=json.dumps(data),
                         publication_date=publication_date,
                         status=publish_status.inv[1])

        db.session.add(db_page)
        db.session.commit()
        return db_page

    def get_topics(self):
        pages = DbPage.query.filter_by(page_type='topic').all()
        return pages

    # TODO remove
    def get_subtopics(self, page):
        subtopic_guids = self.store.get_subtopics(page)
        subtopics = []
        for guid in subtopic_guids:
            st = self.store.get(guid)
            measure_guids = self.store.get_measures(st)
            measures = []
            for m_guid in measure_guids:
                m = self.store.get(m_guid)
                measures.append(m)
            subtopics.append({'subtopic': st, 'measures': measures})
        return subtopics

    def get_pages(self):
        return DbPage.query.all()

    def get_pages_by_type(self, page_type):
        return DbPage.query.filter_by(page_type=page_type).all()

    def get_page(self, guid):
        try:
            page = DbPage.query.filter_by(guid=guid).one()
            return page
        except NoResultFound as e:
            self.logger.exception(e)
            raise PageNotFoundException

    # TODO add error handling for db update
    def create_dimension(self, page, title, time_period, summary, suppression_rules, disclosure_control,
                         type_of_statistic, location, source, user):

        guid = slugify(title).replace('-', '_')

        try:
            self.get_dimension(page, guid)
            raise DimensionAlreadyExists
        except DimensionNotFoundException:
            self.logger.exception('Dimension with guid %s does not exist ok to proceed', guid)
            # dimension = Dimension(guid=guid, title=title, time_period=time_period, summary=summary,
            #                       suppression_rules=suppression_rules, disclosure_control=disclosure_control,
            #                       type_of_statistic=type_of_statistic, location=location, source=source)

            db_dimension = DbDimension(guid=guid,
                                       measure=page.guid,
                                       title=title,
                                       time_period=time_period,
                                       summary=summary,
                                       suppression_rules=suppression_rules,
                                       disclosure_control=disclosure_control,
                                       type_of_statistic=type_of_statistic,
                                       location=location,
                                       source=source)
            db.session.add(db_dimension)
            db.session.commit()
            return db_dimension

    # TODO add error handling for db update
    def update_measure_dimension(self, measure_page, dimension, post_data):
        if measure_page.not_editable():
            message = 'Error updating page "{}" - only pages in DRAFT or REJECT can be edited'.format(measure_page.guid)
            self.logger.error(message)
            raise PageUnEditable(message)

        data = {}
        if 'chartObject' in post_data:
            data['chart'] = post_data['chartObject']
            data['chart_source_data'] = post_data['source']

        if 'tableObject' in post_data:
            data['table'] = post_data['tableObject']
            data['table_source_data'] = post_data['source']

        page_service.update_dimension(measure_page, dimension, data)

    # TODO change to use db
    def delete_dimension(self, page, guid, user):
        if page.not_editable():
            message = 'Error updating page "{}" - only pages in DRAFT or REJECT can be edited'.format(page.guid)
            self.logger.error(message)
            raise PageUnEditable(message)

        dimension = page.get_dimension(guid)

        db.session.delete(dimension)
        db.session.commit()

    # TODO add error handling for db update
    def update_dimension(self, measure_page, dimension, data):
        dimension.title = data['title'] if 'title' in data else dimension.title
        dimension.time_period = data['time_period'] if 'time_period' in data else dimension.time_period
        dimension.summary = data['summary'] if 'summary' in data else dimension.summary
        dimension.chart = data['chart'] if 'chart' in data else dimension.chart
        dimension.table = data['table'] if 'table' in data else dimension.table
        dimension.suppression_rules = data['suppression_rules'] \
            if 'suppression_rules' in data else dimension.suppression_rules
        dimension.disclosure_control = data['disclosure_control'] \
            if 'disclosure_control' in data else dimension.disclosure_control
        dimension.type_of_statistic = data['type_of_statistic'] \
            if 'type_of_statistic' in data else dimension.type_of_statistic
        dimension.location = data['location'] if 'location' in data else dimension.location
        dimension.source = data['source'] if 'source' in data else dimension.source
        if dimension.chart and data.get('chart_source_data') is not None:
            dimension.chart_source_data = json.dumps(data.get('chart_source_data'))
        if dimension.table and data.get('table_source_data') is not None:
            dimension.table_source_data = json.dumps(data.get('table_source_data'))

        db.session.add(dimension)
        db.session.commit()

    def delete_chart(self, measure_page, dimension):
        dimension.chart = ''
        dimension.chart_source_data = ''
        db.session.add(dimension)
        db.session.commit()

    def delete_table(self, measure_page, dimension):
        dimension.table = ''
        dimension.table_source_data = ''
        db.session.add(dimension)
        db.session.commit()

    def get_dimension(self, page, guid):
        try:
            page = DbDimension.query.filter_by(guid=guid).one()
            return page
        except NoResultFound as e:
            self.logger.exception(e)
            raise DimensionNotFoundException

    # TODO db error handling
    def update_page(self, page, data, message=None):
        if page.not_editable():
            message = 'Error updating page "{}" - only pages in DRAFT or REJECT can be edited'.format(page.guid)
            self.logger.error(message)
            raise PageUnEditable(message)
        else:
            publication_date = data.pop('publication_date')
            for key, value in data.items():
                setattr(page, key, value)

            page.publication_date = publication_date

            if page.publish_status() == "REJECTED":
                new_status = publish_status.inv[1]
                page.status = new_status

        db.session.add(page)
        db.session.commit()

    # TODO db error handling
    def next_state(self, slug):
        page = self.get_page(slug)
        message = page.next_state()
        db.session.add(page)
        db.session.commit()
        self.logger.info(message)
        return page

    # TODO db error handling
    def save_page(self, page):
        db.session.add(page)
        db.session.commit()

    # TODO db error handling
    def reject_page(self, slug, message):
        page = self.get_page(slug)
        message = page.reject()
        db.session.add(page)
        db.session.commit()
        self.logger.info(message)
        return page

    def upload_data(self, page_guid, file):
        page_file_system = file_service.page_system(page_guid)

        with tempfile.TemporaryDirectory() as tmpdirname:
            # read the file to a temporary directory
            tmp_file = '%s/%s' % (tmpdirname, file.filename)
            file.save(tmp_file)

            # and write it to the system
            page_file_system.write(tmp_file, 'source/%s' % secure_filename(file.filename))

    # TODO delete from s3 bucket
    def delete_upload(self, page_guid, file_name):
        page_file_system = file_service.page_system(page_guid)
        page_file_system.delete('source/%s' % file_name)

    def get_page_uploads(self, page_guid):
        page_file_system = file_service.page_system(page_guid)
        return page_file_system.list_files('source')

    def get_url_for_file(self, page_guid, file_name):
        page_file_system = file_service.page_system(page_guid)
        return page_file_system.url_for_file('source/%s' % file_name)

    def get_page_by_uri(self, subtopic, measure):
        page = DbPage.query.filter_by(uri=measure, parent_guid=subtopic).one()
        return page

    def mark_page_published(self, page):
        page.publication_date = date.today()
        page.published = True
        message = 'page "{}" published on "{}"'.format(page.guid, page.publication_date.strftime('%Y-%m-%d'))
        self.logger.info(message)
        db.session.add(page)
        db.session.commit()


page_service = PageService()
