from flask import redirect, request, flash, url_for, current_app
from flask_login import current_user
from ..utils import can_manage_poem
from sqlalchemy.exc import OperationalError, IntegrityError
from ..models import Poet, Poem, Category, Stanza, Comment, User


class PoemsController:

    RATINGS = [(0, 1), (1, 3), (3, 5)]

    def get_args(self, *args, **kwargs):
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
    
    def create_category(self, data):
        try:
            Category.create(**data)

            flash(f'Successfully created category {data["name"]}')
            return True
        except:
            flash(f'Failed to create category {data["name"]}')
        
        return False
    
    def get_categories(self):
        categories = Category.find_all()
        return [(category.id, category.poems.count()) for category in categories]
    
    def create_poem(self, data: dict):
        poet = Poet.find_by(user_id=current_user.id, one=True)
        category_id = Category.get_id(data.pop('category'))

        data.update({
            'category_id': category_id,
            'author_id': poet.id
        })
        poem = None

        try:
            # create poem
            poem = Poem.create(return_=True, **data)
            flash('You have successfully started a new poem; what courage!')
        except (OperationalError, IntegrityError) as e:
            if isinstance(e, IntegrityError):
                message = 'Poem with given title already exists'
            else:
                message = 'Failed to create poem due to connection error'
            
            flash(message, 'error')
        
        return poem
    
    def get_poem(self, poem_id=None, slugname=None):
        if slugname is not None:
            poem = Poem.find_poem_by_slug(slugname)
        else:
            poem = Poem.find_by(id=poem_id, one=True)
        
        if poem is not None:
            if current_user.is_anonymous and poem.premium:
                flash('This poem is only accessible to registered users.')
                return None
            
            if not poem.published:
                if current_user.is_anonymous or not poem.is_accessible:
                    flash('This poem is not accessible now. Come back later', 'error')
                    return None
        
        return poem
    
    def add_comment_to_poem(self, poem, comment):
        try:
            data = {
                'user_id': current_user.id,
                'poem_id': poem.id,
                'comment': comment
            }

            Comment.create(**data)
            flash('Your comment has made its mark on the poem 😊')
        except IntegrityError as e:
            flash('You have already added this comment', 'error')
    
    def get_poet(self, poem_id=None):
        poet = None
        message = ''

        if poem_id is None:
            poet = Poet.find_by(user_id=current_user.id, one=True)

            if poet is None:
                message = 'You are not a poet. Go to your profile page to create a poet account'
        else:
            poem = Poem.find_by(id=poem_id, one=True)

            if poem is None:
                message = 'A poem with given id does not exist'
            else:
                poet = Poet.find_by(id=poem.author_id, one=True)
                
                if poet is None:
                    message = 'There is no author associated with this poem'
        
        if poet:
            poems = poet.poems.filter(Poem.id != poem_id)

            if poet.user_id != current_user.id:
                poems = poems.filter_by(published=True)
            
            poems = poems.order_by(*self.__get_ordering_list('RECENT')).limit(
                current_app.config.get('FLASK_POEMS_PER_PAGE', 5)
            ).all()

            return poet, poems
        
        flash(message, 'error')
        return False
    
    def delete_poem(self, poem_id):
        if not can_manage_poem(poem_id):
            flash("Don't be a sly; you cannot control what you don't have!", 'error')
            return False
        
        poem = Poem.find_by(id=poem_id, one=True)

        if poem is None:
            flash('There is no poem with given id', 'error')
            return False
        
        poem.delete()
        flash(f'"{poem.title}" is gone 🥹; are you sure you really wanted this?')
        
        return True
    
    def create_stanza(self, poem_id, index, content):
        stanza = Stanza.find_by(index=index, poem_id=poem_id, one=True)

        if stanza is not None:
            flash(f'This poem already has stanza {stanza.index}', 'error')
            return False
        
        # create new stanza
        Stanza.create(index=index, content=content, poem_id=poem_id)

        flash(f'New stanza has been added to this poem')
        return True
    
    def delete_stanza(self, poem_id, stanza_id):
        stanza = Stanza.find_by(id=stanza_id, poem_id=poem_id, one=True)
        
        if not stanza:
            flash(f'This poem does not have stanza {stanza_id}', 'error')
            return False
        
        # delete stanza from poem
        stanza.delete()

        flash(f'Stanza {stanza.index} has been removed from this poem')
        return True
