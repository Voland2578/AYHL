from flask import Blueprint, render_template
from . import admin
@admin.route('/admin')
def admin_index():
    return render_template('admin.html')
 

