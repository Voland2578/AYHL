from flask import Blueprint, render_template,jsonify
from . import clientapp

tasks = [
     {
         'id': 1,
         'title': u'Buy groceries',
         'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
         'done': False
     },
     {
         'id': 2,
         'title': u'Learn Python',
         'description': u'Need to find a good Python tutorial on the web',
         'done': False
     }
 ]

@clientapp.route('/json')
def dump_json():
    return jsonify({'tasks': tasks})    
 
@clientapp.route('/view')
def client_index():
    return render_template('hockey_stats.html')

