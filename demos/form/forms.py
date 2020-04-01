# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, IntegerField, \
    TextAreaField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Length, ValidationError, Email


# 4.2.1 basic form example
class LoginForm(FlaskForm):     # Field 字段       实例化字段类参数 p107
    username = StringField('Username', validators=[DataRequired()])     # 文本字段
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    # 密码字段  validators为一个列表，包含一系列验证器
    remember = BooleanField('Remember me')     # 复选框字段
    submit = SubmitField('Log in')     # 提交按钮字段
    # 每个字段属性通过实例化WTForms提供的字段类表示，属性名称将作为HTML<input>的name及id属性值,小写的那个
    # 大小写敏感 不能以 _ 和 validate 开头


# custom validator 自定义验证器
class FortyTwoForm(FlaskForm):
    answer = IntegerField('The Number')
    submit = SubmitField()

    def validate_answer(form, field):   # 方法命名为 validate_字段属性名 会自动调用其进行验证
        # form 为表单实例  field 为字段对象
        if field.data != 42:
            raise ValidationError('Must be 42.')


# upload form
class UploadForm(FlaskForm):
    photo = FileField('Upload Image', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    # 上传字段    FileRequired() 是否包含文件对象    FileAllowed()验证文件类型，允许的后缀名list
    submit = SubmitField()


# multiple files upload form
class MultiUploadForm(FlaskForm):
    photo = MultipleFileField('Upload Image', validators=[DataRequired()])
    submit = SubmitField()


# multiple submit button
class NewPostForm(FlaskForm):   # 两个提交按钮
    title = StringField('Title', validators=[DataRequired(), Length(1, 50)])
    body = TextAreaField('Body', validators=[DataRequired()])
    save = SubmitField('Save')
    publish = SubmitField('Publish')


# 为两个表单的提交字段设置不同的名字  思路 通过提交按钮判断
# 登陆表单
class SigninForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit1 = SubmitField('Sign in')


# 注册表单
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit2 = SubmitField('Register')


# 思路 分离表单的渲染和验证 表单提交可用同一个名称
class SigninForm2(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 24)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit = SubmitField()


class RegisterForm2(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 24)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit = SubmitField()


# CKEditor Form 文章表单
class RichTextForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 50)])
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Publish')
