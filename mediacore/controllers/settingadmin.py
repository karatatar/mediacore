from tg import config, request, response, tmpl_context
from sqlalchemy import orm, sql
from repoze.what.predicates import has_permission

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.lib import helpers
from mediacore.model import DBSession, fetch_row, Setting
from mediacore.forms.settings import SettingsForm

settings_form = SettingsForm(action=url_for(controller='/settingadmin',
                                            action='save'))


class SettingadminController(BaseController):
    allow_only = has_permission('admin')

    @expose()
    def index(self, section='topics', **kwargs):
        redirect(controller='categoryadmin', category=section)


    @expose('mediacore.templates.admin.settings.edit')
    def edit(self, **kwargs):
        """Display the :class:`~mediacore.forms.settings.SettingsForm`.

        :rtype: dict
        :returns:
            settings_form
                The :class:`~mediacore.forms.settings.SettingsForm` instance.
            settings_values
                ``dict`` form values

        """
        if tmpl_context.action == 'save' and len(kwargs) > 0:
            # Use the values from error_handler or GET for new users
            settings_values = dict(
                email = dict(
                    media_uploaded = kwargs['email.media_uploaded'],
                    comment_posted = kwargs['email.comment_posted'],
                    support_requests = kwargs['email.support_requests'],
                    send_from = kwargs['email.send_from'],
                ),
#                ftp = dict(
#                    server = kwargs['ftp.server'],
#                    username = kwargs['ftp.username'],
#                    upload_path = kwargs['ftp.upload_path'],
#                    download_url = kwargs['ftp.download_url'],
#                ),
                legal_wording = dict(
                    user_uploads = kwargs['legal_wording.user_uploads'],
                ),
            )
            settings_values = kwargs
            settings_values['ftp.password'] =  settings_values['ftp.confirm_password'] = None
        else:
            settings = self._fetch_keyed_settings()
            settings_values = dict(
                email = dict(
                    media_uploaded = settings['email_media_uploaded'].value,
                    comment_posted = settings['email_comment_posted'].value,
                    support_requests = settings['email_support_requests'].value,
                    send_from = settings['email_send_from'].value,
                ),
#                ftp = dict(
#                    server = settings['ftp_server'].value,
#                    username = settings['ftp_username'].value,
#                    upload_path = settings['ftp_upload_path'].value,
#                    download_url = settings['ftp_download_url'].value,
#                ),
                legal_wording = dict(
                    user_uploads = settings['wording_user_uploads'].value,
                ),
            )

        return dict(
            settings_form = settings_form,
            settings_values = settings_values,
        )

    @expose()
    @validate(settings_form, error_handler=edit)
    def save(self, email, legal_wording, **kwargs):
        """Save :class:`~mediacore.forms.settings.SettingsForm`.

        Redirects back to :meth:`edit` after successful editing.

        """
        settings = self._fetch_keyed_settings()
        settings['email_media_uploaded'].value = email['media_uploaded']
        settings['email_comment_posted'].value = email['comment_posted']
        settings['email_support_requests'].value = email['support_requests']
        settings['email_send_from'].value = email['send_from']
#        settings['ftp_server'].value = ftp['server']
#        settings['ftp_username'].value = ftp['username']
#        if ftp['password'] is not None and ftp['password'] != '':
#            settings['ftp_password'].value = ftp['password']
#        settings['ftp_upload_path'].value = ftp['upload_path']
#        settings['ftp_download_url'].value = ftp['download_url']
        settings['wording_user_uploads'].value = legal_wording['user_uploads']

        DBSession.add_all(settings.values())
        DBSession.flush()
        redirect(action='edit')

    def _fetch_keyed_settings(self):
        """Return a dictionary of settings keyed by the setting.key."""
        settings = DBSession.query(Setting).all()
        return dict((setting.key, setting) for setting in settings)