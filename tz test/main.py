from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, table
from sqlalchemy.orm import relationship
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tz.db'
db = SQLAlchemy(app)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), nullable = False)
    date = db.Column(db.DateTime, default = datetime.now)
    value = db.Column(db.Integer, default = 0)
    connected_good = relationship("Good")
    connected_temporal_begining_date = relationship("Temporal_Begining_Category")
    connected_temporal_ending_date = relationship("Temporal_Ending_Category")
    parent_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Category %r>' % self.id


class Good(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), nullable = False)
    price = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default = datetime.now)
    parent_id = db.Column(db.Integer, ForeignKey("category.id"))
    connected_temporal_begining_date = relationship("Temporal_Begining_Good")
    connected_temporal_ending_date = relationship("Temporal_Ending_Good")

    def __repr__(self):
        return '<Good %r>' % self.id


class Temporal_Begining_Good(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    begining_date = db.Column(db.DateTime, default = datetime.now)
    parent_good = db.Column(db.Integer, ForeignKey("good.id"))

    def __repr__(self):
        return '<Tempoal_Beggining_Good %r>' % self.id

class Temporal_Ending_Good(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    ending_date = db.Column(db.DateTime, default = datetime.now)
    parent_good = db.Column(db.Integer, ForeignKey("good.id"))

    def __repr__(self):
        return '<Tempoal_Ending_Good %r>' % self.id

class Temporal_Begining_Category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    begining_date = db.Column(db.DateTime, default = datetime.now)
    parent_category = db.Column(db.Integer, ForeignKey("category.id"))

    def __repr__(self):
        return '<Tempoal_Beggining_Category %r>' % self.id

class Temporal_Ending_Category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    ending_date = db.Column(db.DateTime, default = datetime.now)
    parent_category = db.Column(db.Integer, ForeignKey("category.id"))

    def __repr__(self):
        return '<Tempoal_Ending_Category %r>' % self.id




@app.route('/log_admin', methods=['POST'])
def log_admin():
    pass

@app.route('/log_user', methods=['POST'])
def log_user():
    pass

@app.route('/')
@app.route('/home')
def home_pg():
    return render_template('home.html')

@app.route('/delete/<int:id>', methods = ['POST', 'GET'])
def delete_pg(id):
    item = Good.query.get(id)
    if item==None:
        item = Category.query.get(id)
        if item==None:
                return render_template('Error.html', text='Элемент с id ' + str(id) + ' не найден')
        else:
            try:
                delete_category(item)
                return render_template('delete.html')
            except:
                return render_template('Error.html', text = 'При удалении элемента произошла ошибка ' + str(item))
    else:
        try:
            db.session.delete(item)
            db.session.commit()
            times = Temporal_Ending_Good.query.filter(Temporal_Ending_Good.parent_good == id).all()
            for time in times:
                db.session.delete(time)
                db.session.commit()
            times = Temporal_Begining_Good.query.filter(Temporal_Begining_Good.parent_good == id).all()
            for time in times:
                db.session.delete(time)
                db.session.commit()
            return render_template('delete.html')
        except:
            return render_template('Error.html', text='При удалении элемента произошла ошибка ' + str(item))


@app.route('/imports', methods = ['POST', 'GET'])
def imports_pg():
    return render_template('imports.html')

@app.route('/check', methods = ['POST'])
def add_to_db_pg():
    id = request.form['id']
    item = Good.query.get(id)
    if item==None:
        item = Category.query.get(id)
        if item==None:
            name = request.form['name']
            if request.form['price']=='':
                temp = Temporal_Begining_Category(name = 'added to others', parent_category=id)
                if request.form['parent_id']=='':
                    category = Category(id = id, name = name)
                else:
                    parent_id = request.form['parent_id']
                    category = Category(id = id, name = name, parent_id = parent_id)
                db.session.add(category)
                db.session.commit()
                db.session.add(temp)
                db.session.commit()
            else:
                price = request.form['price']
                temp = Temporal_Begining_Good(name = 'added to others', parent_good = id)
                if request.form['parent_id']=='':
                    good = Good(id = id, name = name, price = price)
                else:
                    parent_id = request.form['parent_id']
                    good = Good(id = id, name = name, price = price, parent_id = parent_id)
                db.session.add(good)
                db.session.commit()
                db.session.add(temp)
                db.session.commit()
        else:
            text = ''
            f = False
            if request.form['parent_id']!='':
                parent_id=request.form['parent_id']
                if str(parent_id)!=str(item.parent_id):
                    text+='id родителя ' + str(item.parent_id) + ' -> ' + parent_id + ' | '
                    item.date=datetime.now()
                    item.parent_id=parent_id
                    db.session.commit()
                    f = True
            if request.form['name']!='':
                name = request.form['name']
                if name!=item.name:
                    text+='Наименование ' + str(item.name) + ' -> ' + name
                    item.name=name
                    item.date = datetime.now()
                    db.session.commit()
                    f=True
            if f:
                temps = Temporal_Begining_Category.query.filter(Temporal_Begining_Category.parent_category == id).all()
                temp_end = Temporal_Ending_Category(name = temps[len(temps)-1].name, parent_category = id)
                db.session.add(temp_end)
                db.session.commit()
                temp_beg = Temporal_Begining_Category(name = text, parent_category = id)
                db.session.add(temp_beg)
                db.session.commit()
    else:
        text = ''
        f=False
        if request.form['parent_id']!='':
            parent_id = request.form['parent_id']
            if str(parent_id)!=str(item.parent_id):
                text+='id родителя ' + str(item.parent_id) + ' -> ' + str(parent_id) + ' | '
                item.parent_id = parent_id
                item.date = datetime.now()
                db.session.commit()
                f=True
        if request.form['name']!='':
            name = request.form['name']
            if name!=item.name:
                text+='Наименование ' + item.name + ' -> ' + name + ' | '
                item.name = name
                item.date = datetime.now()
                db.session.commit()
                f=True
        if request.form['price']!='':
            price = request.form['price']
            if str(price)!=str(item.price):
                text+='Цена ' + str(item.price) + ' -> ' + price
                item.price = price
                item.date = datetime.now()
                db.session.commit()
                f=True
        if f:
            temps = Temporal_Begining_Good.query.filter(Temporal_Begining_Good.parent_good == id).all()
            temp_end = Temporal_Ending_Good(name = temps[len(temps)-1].name, parent_good = id)
            db.session.add(temp_end)
            db.session.commit()
            temp_beg = Temporal_Begining_Good(name = text, parent_good = id)
            db.session.add(temp_beg)
            db.session.commit()
    return render_template('imports.html')



@app.route('/nodes/<int:id>')
def nodes_pg(id):
    items = []
    for good in Good.query.all():
        if id ==good.id:
            items.append(good)
    if items==[]:
        for category in Category.query.all():
            if id == category.id:
                items.append(category)
        if items==[]:
            return render_template('Error.html', text='Элемент с id ' + str(id) + ' не найден')
        else:
            childs = []
            for good in Good.query.all():
                if good.parent_id==items[0].id:
                    childs.append(good)
            items[0].value = count_value(items[0])[1]/count_value(items[0])[0]
            db.session.commit()
            for category in Category.query.all():
                if category.parent_id==items[0].id:
                    childs.append(category)
            return render_template('nodes.html', items=items[0], category='c', childs = childs)
    else:
        return render_template('nodes.html', items=items[0], category = 'g')

@app.route('/sales')
def sales_pg():
    goods = Good.query.order_by(Good.date.desc()).all()
    items = []
    for good in goods:
        t = datetime.now()
        t = (t - good.date).seconds
        if t<+24*60*60:
            items.append(good)
    return render_template('sales.html', goods = items)


@app.route('/node/<int:id>/statistic')
def statistic_pg(id):
    item = Good.query.get(id)
    if item==None:
        item = Category.query.get(id)
        if item==None:
            return render_template('Error.html', text = 'Элемент с id ' + str(id) + ' не найден')
        else:
            temps_beg=Temporal_Begining_Category.query.filter(Temporal_Begining_Category.parent_category == id).all()
            temps_end=Temporal_Ending_Category.query.filter(Temporal_Ending_Category==id).all()
            counter = len(temps_end)
            category = 'c'
            item.value = count_value(item)[1]/count_value(item)[0]
            db.session.commit()
            return render_template('statistic.html', temps_beg=temps_beg, temps_end=temps_end, counter=counter, item = item, category = category)
    else:
        temps_beg=Temporal_Begining_Good.query.filter(Temporal_Begining_Good.parent_good == id).all()
        temps_end=Temporal_Ending_Good.query.filter(Temporal_Ending_Good.parent_good==id).all()
        counter = len(temps_end)
        category = 'g'
        return render_template('statistic.html', temps_beg = temps_beg, temps_end = temps_end, counter=counter, item = item, category = category)


def delete_category(category):
    times = Temporal_Begining_Category.query.filter(Temporal_Begining_Category.parent_category == category.id).all()
    for time in times:
        db.session.delete(time)
        db.session.commit()
    times = Temporal_Ending_Category.query.filter(Temporal_Ending_Category.parent_category == category.id).all()
    for time in times:
        db.session.delete(time)
        db.session.commit()
    childs = Good.query.filter(Good.parent_id == category.id).all()
    for child in childs:
        times = Temporal_Begining_Good.query.filter(Temporal_Begining_Good.parent_good == child.id).all()
        for time in times:
            db.session.delete(time)
            db.session.commit()
        times = Temporal_Ending_Good.query.filter(Temporal_Ending_Good.parent_good == child.id).all()
        for time in times:
            db.session.delete(time)
            db.session.commit()
        db.session.delete(child)
        db.session.commit()
    childs = Category.query.filter(Category.parent_id == category.id).all()
    if childs != None:
        for child in childs:
            delete_category(child)
    db.session.delete(category)
    db.session.commit()

def count_value(category):
    goods = Good.query.filter(Good.parent_id == category.id).all()
    value=0
    counter=0
    for good in goods:
        value+=good.price
        counter+=1
    childs=Category.query.filter(Category.parent_id == category.id).all()
    if childs!=None:
        for child in childs:
            counter+=count_value(child)[0]
            value+=count_value(child)[1]
    return [counter, value]


if (__name__ == '__main__'):
    app.run(debug=True, host = '0.0.0.0')
