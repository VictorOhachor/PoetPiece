from flask import render_template, redirect, request, flash, url_for
from flask.views import MethodView
from flask_login import login_required, current_user
from . import poems
from .controllers import PoemsController
from .forms import (PoemForm, CategoryForm, StanzaForm,
                    CommentForm, FilterPoemForm)
from ..models import Poet, Poem, Category, Stanza, Comment
from ..utils import is_poet, can_manage_poem, is_verified_poet

# Intitialize the controller for this view
controllers = PoemsController()


class IndexView(MethodView):
    def get(self):
        """Get all poems from the database, filter them according and paginate them."""
        context = {}

        request_args = controllers.get_args(**{
            'category': { 'type': str, 'default': '' },
            'page': { 'type': int, 'default': 1 },
        })

        # get categories
        context['all_category_names'] = [c.name for c in Category.find_all() if c.poems.all()]
        # get pagination object
        context['pagination'] = controllers.get_poems(**request_args)
        # get the poems returned from the pagination object
        context['poems'] = context['pagination'].items

        return render_template('poems/index.html', **context)


class SearchPoemsView(MethodView):
    def get(self):
        """Search and filter through the poems returned"""
        context = {
            'form': FilterPoemForm(request.args),
            'results': controllers.search(),
        }

        return render_template('poems/search_poems.html', **context)


class CategoryMutationView(MethodView):
    decorators = [is_poet]

    def get(self):
        """Get the page that displays the categories and the form for creating a new category."""
        context = {
            'form': CategoryForm(),
            'categories': None
        }

        # get the category id from the query parameters
        category_id = controllers.get_args('category_id')['category_id']

        if category_id:
            category = Category.find_by(id=category_id, one=True)

            if category and category.poems.count() == 0:
                category.delete()
                flash(f'Successfully deleted category, {category.name}')
            else:
                flash('There are poems under this category, hence cannot proceed!', 'error')
            return redirect(url_for('.mutate_categories'))

        # get categories ids and no of poems
        result = controllers.get_categories()

        context['categories'] = [{
            'category': Category.find_by(id=category_id, one=True),
            'no_poems': no_poems} for category_id, no_poems in result
        ]

        return render_template('poems/categories.html', **context)
    
    def post(self):
        """Create a new category"""
        form = CategoryForm()
        # create category
        controllers.create_category(form)

        return redirect(request.referrer)


class PoemCreationView(MethodView):
    decorators = [is_poet]

    def get(self):
        """Display poem creation form page"""
        form = PoemForm()
        return render_template('poems/create_poem.html', form=form)
    
    def post(self):
        """Create a new poem"""
        form = PoemForm()

        if form.validate_on_submit():
            form_data = dict(
                title=form.title.data,
                description=form.description.data,
                premium=form.premium.data,
                category=form.category.data
            )

            # create new poem
            poem = controllers.create_poem(form_data)

            if poem:
                return redirect(url_for('.poem_by_slug', slugname=poem.slug))
        return redirect(url_for('.create_poem'))


class PoemView(MethodView):
    def get(self, slugname=None, poem_id=None):
        """Show information about a specific poem"""
        poem = controllers.get_poem(poem_id, slugname)

        if not poem:
            return redirect(url_for('.index'))

        context = {
            'poem': poem,
            'form': CommentForm(),
            'stanzas': poem.stanzas.order_by(Stanza.index).all(),
        }

        return render_template('poems/poem.html', **context)
    
    @login_required
    def post(self, slugname=None, poem_id=None):
        """Add a comment to the poem."""
        form = CommentForm()
        poem = controllers.get_poem(poem_id, slugname)

        if form.validate_on_submit():
            if poem is not None:
                # add comment to the poem
                controllers.add_comment_to_poem(poem, form.comment.data)
        
        return redirect(url_for('.poem_by_id', poem_id=poem.id))


class PoetView(MethodView):
    decorators = [login_required]

    def get(self, poem_id=None):
        """View the your profile as a poet or the profile of the author of a poem."""
        result = controllers.get_poet(poem_id)

        if not result:
            url = request.referrer if request.referrer != request.url else url_for('.index')
            return redirect(url)
        
        context = {'poet': result[0], 'other_poems': result[1]}
        return render_template('poems/poet.html', **context)


class PoemEditView(MethodView):
    decorators = [is_poet]

    def get(self, poem_id):
        # get poem by id
        poem = Poem.find_by(id=poem_id, one=True)
        # get poem category
        category = Category.find_by(id=poem.category_id, one=True)

        # initialize form
        form = PoemForm(category=category.name, obj=poem)
    
        return render_template('poems/create_poem.html', form=form, update=True)
    
    def post(self, poem_id):
        form = PoemForm()

        if form.validate_on_submit():
            try:
                poem = Poem.find_by(id=poem_id, one=True)
                form.populate_obj(poem)

                category_id = Category.get_id(form.category.data)
                if category_id is None:
                    flash('This category is not supported!', 'error')
                else:
                    poem.category_id = category_id
                    poem.save()

                    flash('Poem has been updated successfully')

                return redirect(url_for('.poem_by_id', poem_id=poem.id))
            except:
                flash('Something went wrong; try again.', 'error')
        
        return redirect(url_for('.edit_poem', poem_id=poem_id))


class PoemDeletionView(MethodView):
    decorators = [is_poet]

    def get(self, poem_id):
        """Delete a poem and all its associated stanzas."""
        success = controllers.delete_poem(poem_id)

        if success:
            return redirect(url_for('.index'))
        
        return redirect(url_for('.poem_by_id', poem_id=poem_id))


class StanzaCreationView(MethodView):
    decorators = [is_poet]

    def get(self, poem_id):
        if not can_manage_poem(poem_id):
            flash('You are unauthorized to create a new Stanza for this poem', 'error')
            return redirect(url_for('.poem_by_id', poem_id=poem_id))
        
        poem = Poem.find_by(id=poem_id, one=True)
        form = StanzaForm(index=poem.stanzas.count() + 1)

        return render_template('poems/add_stanza.html', form=form)
    
    def post(self, poem_id):
        form = StanzaForm()

        if not can_manage_poem(poem_id):
            flash('You are unauthorized to create a new Stanza for this poem', 'error')
            return redirect(url_for('.poem_by_id', poem_id=poem_id))

        if form.validate_on_submit():
            controllers.create_stanza(
                poem_id, form.index.data, form.content.data
            )

            return redirect(url_for('.poem_by_id', poem_id=poem_id))
        
        return redirect(url_for('.add_stanza', poem_id=poem_id))


class StanzaDeletionView(MethodView):
    decorators = [is_poet]

    def get(self, poem_id, stanza_id):
        if not can_manage_poem(poem_id):
            flash('You are unauthorized to create a new Stanza for this poem', 'error')
            return redirect(url_for('.poem_by_id', poem_id=poem_id))
        
        controllers.delete_stanza(poem_id, stanza_id)
        return redirect(url_for('.poem_by_id', poem_id=poem_id))


class StanzaEditView(MethodView):
    decorators = [is_poet]

    def get(self, poem_id, stanza_id):
        if not can_manage_poem(poem_id):
            flash('You are unauthorized to create a new Stanza for this poem', 'error')
            return redirect(url_for('.poem_by_id', poem_id=poem_id))
        
        stanza = Stanza.find_by(id=stanza_id, poem_id=poem_id, one=True)
        if not stanza:
            flash('No stanza found with given id; create new stanza', 'error')
            return redirect(url_for('add_stanza', poem_id=poem_id))
        
        form = StanzaForm(obj=stanza)

        return render_template('poems/add_stanza.html', form=form, update=True)
    
    def post(self, poem_id, stanza_id):
        if not can_manage_poem(poem_id):
            flash('You are unauthorized to create a new Stanza for this poem', 'error')
            return redirect(url_for('.poem_by_id', poem_id=poem_id))
        
        form = StanzaForm()
        stanza = Stanza.find_by(id=stanza_id, poem_id=poem_id, one=True)
        
        if not stanza:
            flash('No stanza found with given id, hence cannot edit.', 'error')
        else:
            if form.validate_on_submit():
                form.populate_obj(stanza)
                stanza.save()

                flash(f'Successfully updated stanza {stanza.index}')
        
        return redirect(url_for('.poem_by_id', poem_id=poem_id))
    

class CommentDeletionView(MethodView):
    decorators = [login_required]

    def get(self, poem_id, comment_id):
        comment = Comment.find_by(id=comment_id, one=True)

        if current_user.id != comment.user_id:
            flash('You are not authorized to delete this comment', 'error')
        else:
            if comment is None:
                flash('No comment with given id exists', 'error')
            else:
                comment.delete()
                flash(f'You have deleted comment "{comment.comment[:10]}..." from this poem')
        
        return redirect(url_for('.poem_by_id', poem_id=poem_id))


class PoemPublishView(MethodView):
    decorators = [is_poet]

    def get(self, poem_id):
        if not can_manage_poem(poem_id):
            flash('You cannot publish/unpublish a poem that is not yours!', 'error')
        else:
            poem = Poem.find_by(id=poem_id, one=True)
            poem.publish()

            flash('Now the world can see your creative piece; bravo!' if poem.published
                else 'You have unpublished your creative piece; do you know?')
        
        return redirect(url_for('.poem_by_id', poem_id=poem_id))


class CompletePoemView(MethodView):
    decorators = [is_poet]

    def get(self, poem_id):
        if not can_manage_poem(poem_id):
            flash('You are not the author of this poem', 'error')
        else:
            poem = Poem.find_by(id=poem_id, one=True)

            if not poem:
                flash('Poem with given id does not exist', 'error')
            else:
                poem.completed = not poem.completed
                poem.save()
                flash('Poem status has been updated')
        
        return redirect(url_for('.poem_by_id', poem_id=poem_id))
