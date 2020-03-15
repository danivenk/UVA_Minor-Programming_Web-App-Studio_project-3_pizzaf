from flask_admin.contrib.sqla import ModelView


class UserView(ModelView):
    column_exclude_list = ["password", ]
