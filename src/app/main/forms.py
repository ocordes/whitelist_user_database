"""

app/main/forms.py

written by: Oliver Cordes 2021-02-17
changed by: Oliver Cordes 2021-02-22

"""


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, \
                    SubmitField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, WhitelistGroup

from wtforms import widgets, SelectMultipleField

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class WhitelistGroupForm(FlaskForm):
    groupname = StringField('Groupname', validators=[DataRequired()])
    role      = SelectField(coerce=int)

    submit = SubmitField('Add')

    def validate_groupname(self, groupname):
        group = WhitelistGroup.query.filter_by(groupname=groupname.data).first()
        if group is not None:
            raise ValidationError('Please use a different group name.')


class DeleteWhitelistGroupForm(FlaskForm):
    remove = SubmitField('Delete')


class AddUserForm(FlaskForm):
    group = SelectField(coerce=int)
    users = TextAreaField(u'User IDs')
    submit = SubmitField('Add')
    
class DeleteWhitelistUserForm(FlaskForm):
    group = SelectField(coerce=int)
    select = SubmitField('Select')
    remove = SubmitField('Delete')
