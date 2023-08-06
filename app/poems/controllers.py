from flask import (render_template, redirect, request,
                   flash, url_for, current_app)
from flask_login import login_required, current_user
from sqlalchemy.sql import func
from . import poems
from .. import db
from .forms import (PoemForm, CategoryForm, StanzaForm,
                    CommentForm, FilterPoemForm)
from ..models import Poet, Poem, Category, Stanza, Comment, User


class PoemsController:

    RATINGS = [(0, 1), (1, 3), (3, 5)]

    def get_args(self, *args, **kwargs: dict[str, dict]):
        query_args = {}

        # Get the query parameters from the request
        for arg in args:
            query_args[arg] = request.args.get(arg)


        # Get the query parameters from the request with more flexibility
        for key, options in kwargs.items():
            arg_type = options.get('type', str)
            arg_default = options.get('default', None)

            query_args[key] = request.args.get(key, arg_default, arg_type)

        return query_args
    
    def __get_ordering_list(self, order_by: str):
        ORDERS = {
            'RECENT': [Poem.created_at.desc(), Poem.updated_at.desc()],
            'POPULAR': [Poem.rating.desc(), Category.name],
            'A-Z': [Poem.title, Poem.updated_at.desc()],
            'Z-A': [Poem.title.desc(), Poem.updated_at],
            'AUTHORS': [Poem.author_id, Poem.rating.desc(), Poem.premium],
        }

        return ORDERS.get(order_by.upper(), 'A-Z')
    
    def __get_published_or_owned_by(self, query):
        if current_user.is_anonymous or not current_user.is_poet:
            query = query.filter(Poem.published == True)
        else:
            poet_id = Poet.find_by(user_id=current_user.id, one=True).id

            # filter out poems that are not published and owned by current user
            query = query.filter(((Poem.author_id == poet_id) & (
                Poem.published == False)) | (Poem.published == True)
            )

        return query
    
    def get_poems(self, category, page, order_by='RECENT'):

        # query both the Poem and Category tables
        query = Poem.join(Category, 'category_id', False)

        # filter out unpublished poems not written by user
        query = self.__get_published_or_owned_by(query)

        if category:
            query = query.filter(Category.name == category)

        return query.order_by(*self.__get_ordering_list(order_by)).paginate(
            page=page, per_page=current_app.config.get('FLASK_POEMS_PER_PAGE', 10),
            error_out=False
        )
    
    def __process_search_query(self, query_params: dict):
        """Process the form data passed and returned a more refined dict data."""
        query_data = {}

        # all search/filter query keys that will be used
        keys = {
            'q': str, 'author_id': str, 'rating': int,
            'completed': bool, 'premium': bool,
        }

        if query_params.get('poet'):
            user = User.find_by_username(query_params['poet'])
            if user:
                query_data['author_id'] = Poet.find_by(user_id=user.id, one=True).id

        for k in keys:
            value = query_params.get(k)

            # convert value to expected type
            try:
                converter = keys[k]

                if not value:
                    continue

                if converter is bool:
                    query_data[k] = True if value == 'True' else False
                else:
                    query_data[k] = converter(value)
            except (TypeError, ValueError):
                continue

        return query_data
    
    def search(self):
        # parse and convert query string into dictionary
        query_params = self.__process_search_query(
            request.args.to_dict(flat=True)
        )

        # initializing database query
        query = Poem.query

        # query by search string
        if query_params.get('q'):
            print(type(query_params.get('q')), 'search string')
            search_string = query_params.pop('q')
            query = query.filter(
                Poem.title.ilike(f'%{search_string}%') | Poem.description.ilike(f'%{search_string}%')
            )
        
        # filter query by rating
        if query_params.get('rating'):
            rating = query_params.pop('rating')

            for r_min, r_max in self.RATINGS:
                if rating <= r_max:
                    query = query.filter((Poem.rating >= r_min) & (Poem.rating <= r_max))
                    break

        if query_params:    
            query = query.filter_by(**query_params)
        
        # remove any unpublished poems that the current user did not compose
        query = self.__get_published_or_owned_by(query)

        return query.order_by(*self.__get_ordering_list('A-Z')).all()
    
    def create_category(self, form):
        category_data = {
            'name': form.name.data,
        }

        if form.description.data:
            category_data['description'] = form.description.data
        
        if form.validate_on_submit():
            try:
                Category.create(**category_data)
                flash(f'Successfully created category {category_data["name"]}')
            except Exception as e:
                print(str(e))
                flash(f'Failed to create category {category_data["name"]}')
    
    def get_categories(self):
        # get all poems and group them by their categories
        categories = Category.find_all()
        # categories = Poem.group_by(
        #     Poem.category_id, func.count(Poem.category_id).label('no_poems'),
        #     group_by=Poem.category_id
        # ).all()

        return [(category.id, category.poems.count()) for category in categories]
