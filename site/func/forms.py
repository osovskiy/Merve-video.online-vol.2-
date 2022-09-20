from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ContactForm(FlaskForm):
    name = StringField("Videos", render_kw={
                       "placeholder": "Paste link from YouTube",
                       "class": "form-control video_input",
                       "id": "formGroupExampleInput"})
