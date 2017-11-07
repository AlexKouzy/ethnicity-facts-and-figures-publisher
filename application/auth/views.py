import datetime
import passwordmeter
from flask import render_template, flash, redirect, url_for, current_app, abort
from flask_mail import Message
from flask_security.decorators import anonymous_user_required
from flask_security.utils import encrypt_password
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from application.auth import auth_blueprint
from application.auth.forms import ForgotPasswordForm
from application import mail, db
from application.auth.models import User, Role
from application.register.forms import SetPasswordForm
from application.utils import admin_required, generate_token, check_token


@auth_blueprint.route('/forgot', methods=['GET', 'POST'])
@anonymous_user_required
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():

        email = form.email.data.strip()
        try:
            User.query.filter_by(email=email).one()
        except (MultipleResultsFound, NoResultFound) as e:
            current_app.logger.error(e)
            flash('Instructions for updating your password have been sent to %s' % email)
            return redirect(url_for('auth.forgot_password'))

        token = generate_token(email, current_app)
        confirmation_url = url_for('auth.reset_password',
                                   token=token,
                                   _external=True)

        html = render_template('auth/email/reset_instructions.html', confirmation_url=confirmation_url)

        msg = Message(html=html,
                      subject="Password reset for the RDU CMS",
                      sender=current_app.config['RDU_EMAIL'],
                      recipients=[form.email.data])
        try:
            mail.send(msg)
            flash('Instructions for updating your password have been sent to %s' % email)

        except Exception as ex:
            flash("Failed to send password reset email to: %s" % email, 'error')
            current_app.logger.error(ex)

        return redirect(url_for('auth.forgot_password'))

    return render_template('auth/forgot_password.html', form=form)


@auth_blueprint.route('/reset/<token>', methods=['GET', 'POST'])
@anonymous_user_required
def reset_password(token):
    email = check_token(token, current_app)
    if not email:
        current_app.logger.info('token has expired.')
        flash('Link has expired', 'error')
        abort(400)

    form = SetPasswordForm()
    user = User.query.filter_by(email=email).first()

    if not user:
        return redirect(url_for('auth.login'))

    if form.validate_on_submit():
        password = form.password.data.strip()

        meter = passwordmeter.Meter(settings=dict(factors='length,variety,phrase,notword,casemix'))
        strength, improvements = meter.test(password)
        if strength < 0.7:
            message = ['Your password is too weak.']
            for key, val in improvements.items():
                message.append(val)

            flash('\n'.join(message), 'error')
            return render_template('auth/reset_password.html',
                                   form=SetPasswordForm(),
                                   token=token,
                                   user=user)

        user.password = encrypt_password(password)

        db.session.add(user)
        db.session.commit()

        internal_role = Role.query.filter_by(name='INTERNAL_USER').one()
        internal_user = internal_role in user.roles

        # TODO send email notification of password reset?

        return render_template('auth/password_updated.html',
                               form=form,
                               token=token,
                               user=user,
                               internal_user=internal_user)

    return render_template('auth/reset_password.html',
                           form=form,
                           token=token,
                           user=user)