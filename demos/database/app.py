# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os
import sys

import click
from flask import Flask
from flask import redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired
# 迁移数据库
# from flask_migrate import Migrate

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# os.getenv() 获取环境变量
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret string')

# 连接数据库 URI格式
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', prefix + os.path.join(app.root_path, 'data.db'))
# print("app.root_path : ", app.root_path)
# app.root_path :  D:\PythonWorkSpace\flask_web\demos\database

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 是否追踪对象的修改 设为 False 关闭警告

db = SQLAlchemy(app)    # 实例化 SQLAlchemy类
# 迁移数据库
# migrate = Migrate(app, db)  # 在db对象创建后调用

# handlers
@app.shell_context_processor    # 注册一个shell上下文处理函数
def make_shell_context():
    # flask shell 执行后 所有app.shell_context_processor装饰器
    # 注册的shell上下文处理函数都会自动执行，将变量推送到Python shell 上下文中
    # 返回包含变量和变量值的字典
    return dict(db=db, Note=Note, Author=Author, Article=Article, Writer=Writer, Book=Book,
                Singer=Singer, Song=Song, Citizen=Citizen, City=City, Capital=Capital,
                Country=Country, Teacher=Teacher, Student=Student, Post=Post, Comment=Comment, Draft=Draft)


# option装饰器为命令添加 --drop 选项
# is_flag=True 将选项声明为布尔值
# --drop 选项 的值作为drop 参数 传入命令函数
@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        # 可添加 确认提示
        # click.confirm('This operation will delete the database, do you want to continue?', abort=True)
        # abort:if this is set to `True` a negative answer aborts the exception by raising: exc:`Abort`.
        # abort：如果这个设置为“True”，一个否定的回答将通过引发:exc:“Abort”中止异常。
        db.drop_all()   # 删除表及数据
    db.create_all()     # 建库和建表  调用create_all() 方法    生成data.db文件
    click.echo('Initialized database.')

# 模型类（表）不是一成不变的，当你添加了新的模型类，或是在模型类中添加了新的字段，甚至是修改了字段的名称或类型，都需要更新表。
# 数据库表并不会随着模型的修改而自动更新
# 不在意数据，最简单方法：先删除 再创建


# Forms
class NewNoteForm(FlaskForm):   # 填写新笔记的表单
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Save')


class EditNoteForm(FlaskForm):  # 更新笔记的表单
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Update')
# 其可通过继承简化
# class EditNoteForm(NewNoteForm):
#     submit = SubmitField('Update')


class DeleteNoteForm(FlaskForm):    # 删除笔记的表单
    submit = SubmitField('Delete')  # 只需要删除按钮来提交表单


# Models
class Note(db.Model):   # 定义 Note 模型类    继承 db.Model 基类
    # 自动根据类名称生成表名称 规则：单个单词转为小写、多个单词转为小写且下划线分割
    # __tablename__ = '' 也可指定
    id = db.Column(db.Integer, primary_key=True)    # 主键 必须定义 由SQLAlchemy管理
    body = db.Column(db.Text)
    # 字段名默认为类属性名

    # optional
    def __repr__(self):     # __repr__会自动生成，这重新定义了
        # 在Python shell 调用模型的对象时，返回字符串
        return '<Note %r>' % self.body
        # %r是一个万能的格式符，它会将后面给的参数原样打印出来，带有类型信息


@app.route('/')
def index():    # 渲染主页对应的模板
    form = DeleteNoteForm()     # 由于删除按钮需要在主页笔记下添加
    notes = Note.query.all()    # 这是为了在主页中列出所有保存的笔记
    return render_template('index.html', notes=notes, form=form)    # 渲染模板 p78


# CRUD Create,创建  Read,查询  Update,更新  Delete,删除

# 创建：1.创建对象  实例化模型类 作为一条记录
# 2. 添加记录到数据库会话
# 3. 提交数据库会话
@app.route('/new', methods=['GET', 'POST'])
def new_note():     # 渲染创建笔记的模板、处理表单的提交
    form = NewNoteForm()
    if form.validate_on_submit():
        body = form.body.data   # form.data 为表单数据字典 其匹配所有字段与对应数据
        # form.body.data 为body字段的数据   form.字段属性名.data 获取对应字段数据
        note = Note(body=body)  # 创建新的Note实例 这使用关键字参数
        db.session.add(note)    # 也可一次添加多条记录 add_all([note1, note2])
        db.session.commit()     # 提交后 才会写入数据库 有id值
        flash('Your note is saved.')    # flash 发送消息
        return redirect(url_for('index'))   # 重定向到 index视图
    return render_template('new_note.html', form=form)


# 查询：模型类.query.过滤方法.查询方法   query属性 附加过滤方法和查询方法 实现查询
# 返回 包含对应数据库记录数据的模型类实例，对实例调用属性获取对应的字段数据
# 查询方法：Note.query.all()  //  Note.query.get(2)  //  Note.query.count()
# 过滤方法可叠加
# filter() 指定规则过滤记录     其余 p150

# 更新：直接赋值给模型类的字段属性来改变值，然后使用commit() 提交修改
# 插入新纪录 或将现有记录添加到会话中 才需要使用 add()，更新时不需要
@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])  # int 变量转换器 p36
def edit_note(note_id):     # 被修改笔记的主键值 id字段
    form = EditNoteForm()
    note = Note.query.get(note_id)  # get获取对应实例
    if form.validate_on_submit():
        note.body = form.body.data
        db.session.commit()
        flash('Your note is updated.')
        return redirect(url_for('index'))
    form.body.data = note.body  # preset form input's value
    # GET请求  需要添加要修改笔记的内容
    return render_template('edit_note.html', form=form)


# 删除：删除和添加相似 把 add() 换为 delete()，再commit()提交修改
@app.route('/delete/<int:note_id>', methods=['POST'])   # methods=['POST'] 只监听POST请求
def delete_note(note_id):
    # 删除操作不能通过GET请求 p155
    form = DeleteNoteForm()
    if form.validate_on_submit():   # 唯一需要被验证的是CSRF令牌
        note = Note.query.get(note_id)
        db.session.delete(note)     # 删除
        db.session.commit()     # 提交数据库会话
        flash('Your note is deleted.')
    else:
        abort(400)  # 返回400错误响应
    return redirect(url_for('index'))


# 定义关系 让不同表之间的字段建立联系   1.创建外键 2.定义关系属性
# one to many 一对多  作者-文章
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    phone = db.Column(db.String(20))
    articles = db.relationship('Article')  # collection
    # 添加关系属性 为集合属性   其类似于查询函数 p161
    # 关系属性在关系的出发侧定义，此处即一对多关系的“一”这一侧。
    # 对特定Author对象调用articles属性会返回所有相关Article对象 返回包含记录的list
    # 关系属性不会作为字段存入数据库

    def __repr__(self):
        return '<Author %r>' % self.name


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True)
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))   # 外键字段由SQLAlchemy管理
    # 外键是(foreign key)用来在A表存储B表的主键值以便和B表建立联系的关系字段。
    # 外键只能存储单一数据（标量），所以外键总是在“多”一侧定义
    # 使用db.ForeignKey类定义外键 传入关系另一侧的表名和主键字段名 author.id
    # author指的是Author模型对应的表名称，而id指的是字段名，即“表名.字段名”。
    # 将article表的author_id的值限制为author表的id列的值

    def __repr__(self):
        return '<Article %r>' % self.title


'''flask shell
# 创建一个作者记录和两个文章记录
>>> foo = Author(name='Foo')
>>> spam = Article(title='Spam')
>>> ham = Article(title='Ham')
>>> db.session.add(foo)
>>> db.session.add(spam)
>>> db.session.add(ham)
# 建立关系的方式：1.为外键字段复制，如：
>>> spam.author_id = 1
>>> ham.author_id = 1
>>> db.session.commit()
>>> foo.articles
# 2.将关系属性赋给实际的对象，
# 集合关系属性可以像列表一样操作，调用append()方法来与一个Article对象建立关系
>>> foo.articles.append(spam)
>>> foo.articles.append(ham)
# 包含Article对象的列表也可以
>>> db.session.commit()
>>> spam.author_id
>>> foo.articles
# 对关系属性调用remove()方法可以与对应的Aritcle对象解除关系 
>>> foo.articles.remove(spam)
# 也可以使用pop()方法操作关系属性，会与关系属性对应的列表的最后一个Aritcle对象解除关系并返回该对象
>>> db.session.commit()
>>> foo.articles
'''


# one to many + bidirectional relationship 一对多 + 双向关系
class Writer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    books = db.relationship('Book', back_populates='writer')    # 获取对应多个Book 记录
    # back_populates参数连接对方 设为关系另一侧的关系属性名

    def __repr__(self):
        return '<Writer %r>' % self.name


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    writer_id = db.Column(db.Integer, db.ForeignKey('writer.id'))
    writer = db.relationship('Writer', back_populates='books')    # 获取对应Writer 记录
    # 返回单个值的关系属性称为标量关系属性

    def __repr__(self):
        return '<Book %r>' % self.name


'''flask shell
# 创建1个Writer和2个Book记录
>>> king = Writer(name='Stephen King')
>>> carrie = Book(name='Carrie')
>>> it = Book(name='IT')
>>> db.session.add(king)
>>> db.session.add(carrie)
>>> db.session.add(it)
>>> db.session.commit()
# 设置双向关系后，除了通过集合属性books来操作关系，也可以使用标量属性writer来进行关系操作。
>>> carrie.writer = king
>>> carrie.writer
>>> king.books
>>> it.writer = king
>>> king.books
# 相对的，将某个Book的writer属性设为None，就会解除与对应Writer对象的关系
>>> carrie.writer = None
>>> king.books
>>> db.session.commit()
# 只需要在关系的一侧操作关系。当为Book对象的writer属性赋值后，
# 对应Writer对象的books属性的返回值也会自动包含这个Book对象。
# 反之，当某个Writer对象被删除时，
# 对应的Book对象的writer属性被调用时的返回值也会被置为空（即NULL，会返回None）。
'''


# one to many + bidirectional relationship + use backref to declare bidirectional relationship
# 使用backref简化双向关系的定义
# 但 显式好过隐式    推荐 back_populates
class Singer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    songs = db.relationship('Song', backref='singer')
    # 以一对多关系为例，backref参数用来自动为关系另一侧添加关系属性，
    # 作为反向引用（back reference），赋予的值会作为关系另一侧的关系属性名称。
    # 将backref参数设为singer，这会同时在Song类中添加了一个singer标量属性。
    # 使用和定义两个关系函数并使用back_populates参数的效果完全相同

    # 某些情况下，希望可以对在关系另一侧的关系属性进行设置，这时就需要使用backref()函数
    # backref() 接收第一个参数为关系另一侧添加的关系属性名，其他关键字参数作为关系另一侧关系函数的参数传入
    # 如：songs = db.relationship('Song', backref=backref('singer', uselist=False))

    def __repr__(self):
        return '<Singer %r>' % self.name


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    singer_id = db.Column(db.Integer, db.ForeignKey('singer.id'))

    def __repr__(self):
        return '<Song %r>' % self.name


# many to one 多对一
# 当建立双向关系时，如果不使用backref，那么一对多和多对一关系模式在定义上完全相同，
# 通常弱化这两种关系的区别，一律称为一对多关系。
class Citizen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City')  # scalar 标量关系属性
    # 关系属性在关系模式的出发侧定义
    # 当出发点在“多”这一侧时，希望在Citizen类中添加一个关系属性city来获取对应的城市对象
    # 因为关系属性返回单个值，称之为标量关系属性
    # 外键总是在“多”一侧定义

    # 当Citizen.city被调用时，SQLAlchemy会根据外键字段city_id存储的值查找对应的City对象并返回
    # 即居民记录对应的城市记录

    def __repr__(self):
        return '<Citizen %r>' % self.name


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    def __repr__(self):
        return '<City %r>' % self.name


# one to one 一对一
# 一对一关系实际上是通过建立双向关系的一对多关系的基础上转化而来。
# 在定义集合属性的关系函数中将uselist参数设为False，这时一对多关系将被转换为一对一关系。
class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    capital = db.relationship('Capital', uselist=False)  # collection -> scalar
    # 标量关系属性
    # uselist=False 使用标量  无法再使用列表语义操作

    def __repr__(self):
        return '<Country %r>' % self.name


class Capital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    country = db.relationship('Country')  # scalar
    # 标量关系属性

    def __repr__(self):
        return '<Capital %r>' % self.name


'''flask shell
>>> china = Country(name='China')
>>> beijing = Capital(name='Beijing')
>>> china.capital = beijing     # 这放在提交前也可以
>>> db.session.add(china)
>>> db.session.add(beijing)
>>> db.session.commit()
>>> china.capital
>>> beijing.country
>>> tokyo = Capital(name='Tokyo')
>>> china.capital.append(tokyo) # 报错
'''

# many to many with association table 多对多 关联表
# 在SQLAlchemy中，要想表示多对多关系，除了关系两侧的模型外，
# 需要创建一个关联表（association table）。
# 关联表不存储数据，只用来存储关系两侧模型的外键对应关系。
association_table = db.Table('association',
                             db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                             db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'))
                             )
# 关联表使用db.Table类定义，传入的第一个参数是关联表的名称。
# 关联表中定义了两个外键字段：teacher_id字段存储Teacher类的主键，student_id存储Student类的主键。
# 借助关联表这个中间人存储的外键对，我们可以把多对多关系分化成两个一对多关系


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    grade = db.Column(db.String(20))
    teachers = db.relationship('Teacher',
                               secondary=association_table,
                               back_populates='students')  # collection
    # 关系属性 需要添加一个secondary参数，把这个值设为关联表的名称。

    def __repr__(self):
        return '<Student %r>' % self.name


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    office = db.Column(db.String(20))
    students = db.relationship('Student',
                               secondary=association_table,
                               back_populates='teachers')  # collection

    def __repr__(self):
        return '<Teacher %r>' % self.name
# 关联表由SQLAlchemy接管
# 通过一样的操作关系属性来建立或解除关系，SQLAlchemy会自动在关联表中创建或删除对应的关联表记录
# 关系属性teachers和students像列表一样操作 添加append()、解除remove()


# cascade 级联操作 是在操作一个对象的同时，对相关的对象也执行某些操作。
class Post(db.Model):   # 帖子
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.Text)
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')  # collection
    # 级联行为通过关系函数relationship()的cascade参数设置
    # 在操作Post对象时，处于附属地位的Comment对象也被相应执行某些操作，
    # 应该在Post类的关系函数中定义级联参数
    # 设置了cascade参数的一侧将被视为父对象，相关的对象则被视为子对象
    # cascade通常使用多个组合值，级联值之间使用逗号分隔 p173
    # all等同于除了delete-orphan以外所有可用值的组合，即save-update、merge、refresh-expire、expunge、delete
    # save-update: 使用db.session.add()方法将Post对象添加到数据库会话时，
    #              那么与Post相关联的Comment对象也将被添加到数据库会话
    # delete: 当某个Post对象被删除时，所有相关的Comment对象都将被删除
    # delete-orphan: 包含delete级联的行为，除此之外，
    #                当某个Post对象(父对象)与某个Comment对象(子对象)解除关系时，
    #                也会删除该Comment对象，这个解除关系的对象被称为孤立对象(orphan object)


class Comment(db.Model):    # 评论
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')  # scalar


# event listening 事件监听
# 通过注册事件监听函数，实现在body列修改时，自动叠加表示被修改次数的edit_time字段。
class Draft(db.Model):  # 草稿
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)   # 正文
    edit_time = db.Column(db.Integer, default=0)    # 编辑次数


# listens_for()装饰器，注册事件回调函数
# 第一个参数targe为监听对象 可以是模型类、类实例或类属性等
# 第二个参数identifier为被监听事件的标识符 有set、append、remove、init_scalar、init_collection等
@db.event.listens_for(Draft.body, 'set')    # 设置某个字段值将触发set事件
def increment_edit_time(target, value, oldvalue, initiator):
    # 被注册的监听函数需要接收对应事件方法的所有参数
    # target参数表示触发事件的模型类实例，使用target.edit_time即可获取我们需要叠加的字段。
    # 其他的参数也需要照常写出，虽然这里没有用到。
    # value表示被设置的值，oldvalue表示被取代的旧值。
    if target.edit_time is not None:
        target.edit_time += 1
    # 当set事件发生在目标对象Draft.body上时，这个监听函数就会被执行，从而自动叠加Draft.edit_time列的值

# same with:
# @db.event.listens_for(Draft.body, 'set', named=True)
# def increment_edit_time(**kwargs):
#     if kwargs['target'].edit_time is not None:
#         kwargs['target'].edit_time += 1
# 在listen_for()装饰器中将关键字参数named 设为True，
# 可以在监听函数中接收**kwargs作为参数（可变长关键字参数）
# 在函数中可以使用参数名作为键来从**kwargs字典获取对应的参数值


'''flask shell
>>> draft = Draft(body='init')
>>> db.session.add(draft)
>>> db.session.commit()
>>> draft.edit_time
0 
>>> draft.body ='edited'
>>> draft.edit_time
1 
>>> draft.body ='edited again'
>>> draft.edit_time
2 
>>> draft.body ='edited again again'
>>> draft.edit_time
3 
>>> db.session.commit()
'''