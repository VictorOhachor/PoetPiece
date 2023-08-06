from flask import (render_template, redirect, request,
                   flash, url_for, current_app)
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


@poems.route('/categories/new', methods=['GET', 'POST'])
@is_verified_poet
def create_category():
    """Add new category."""

    form = CategoryForm()

    if form.validate_on_submit():
        category = Category(name=form.name.data,
                            description=form.description.data)
        category.save()

        # redirect back to home
        flash(f'Created a new category ({form.name.data}).', 'info')
        return redirect(url_for('.index'))
    return render_template('poems/create_category.html', form=form)


@poems.route('/poems/new', methods=['GET', 'POST'])
@is_poet
def create_poem():
    """Create a new poem."""
    # initialize create poem form
    form = PoemForm()

    if form.validate_on_submit():
        poet = Poet.find_by(user_id=current_user.id, one=True)
        category = Category.find_by(name=form.category.data, one=True)

        # create poem
        poem = Poem(author_id=poet.id, title=form.title.data,
                    description=form.description.data,
                    category_id=category.id,
                    premium=form.premium.data)
        poem.save()

        # redirect to poem page
        flash('Successfully created poem. What a courage!', 'info')
        return redirect(url_for('.poem', slugname=poem.slug))
    return render_template('poems/create_poem.html', form=form)


@poems.route('/p/<string:slugname>', methods=['GET', 'POST'])
@poems.route('/poems/<string:poem_id>', methods=['GET', 'POST'])
def poem(slugname=None, poem_id=None):
    """Show details about poem with given id."""
    if slugname:
        poem = Poem.find_poem_by_slug(slugname)
    else:
        poem = Poem.find_by(id=poem_id, one=True)

    if not poem:
        flash('Poem with such id not found.', 'error')
        return redirect(url_for('.index'))

    context = {
        'poem': poem,
        'form': CommentForm(),
        'stanzas': Stanza.find_order_by(Stanza.index, poem_id=poem.id)
    }

    if current_user.is_anonymous and context['poem'].premium:
        flash('Sorry, this poem is only available to registered users.',
              'error')
        return redirect(url_for('.index'))

    if not context['poem'].published:
        if current_user.is_anonymous or not context['poem'].is_accessible:
            flash('This poem is not available to you.', 'error')
            return redirect(url_for('.index'))

    if context['form'].validate_on_submit():
        Comment.create(
            user_id=current_user.id,
            poem_id=context['poem'].id,
            comment=context['form'].comment.data
        )

        flash('Your comment has been added successfully', 'info')
        return redirect(url_for('.poem', poem_id=context['poem'].id))

    return render_template('poems/poem.html', **context)


@poems.route('/me/view-as-user')
@poems.route('/poems/<string:poem_id>/view-poet')
@login_required
def view_poet(poem_id=None):
    """View the profile of the author of a poem."""
    context = {
        'poet': None,
        'other_poems': None
    }

    if not poem_id:
        context['poet'] = Poet.find_by(user_id=current_user.id, one=True)
        if not context['poet']:
            flash('This user is no poet!', 'error')
            return redirect(url_for('main.me'))
    else:
        poem = Poem.find_by(id=poem_id, one=True)
        if not poem:
            flash('A poem with given id does not exist.', 'error')
            return redirect(url_for('poems.index'))

        # get poet data from db
        context['poet'] = Poet.find_by(id=poem.author_id, one=True)
        if not context['poet']:
            flash('This poem is no longer owned by a poet. The poet must '
                  'have deleted their account.', 'error')
            return redirect(url_for('poems.index'))

    # get other poems written by same poet
    context['other_poems'] = context['poet'].poems.filter(Poem.id != poem_id)

    # filter by published when other user aside the poet is viewing page
    if context['poet'].user_id != current_user.id:
        context['other_poems'] = context['other_poems'].filter_by(
            published=True)

    context['other_poems'] = context['other_poems'].order_by(
        Poem.rating.desc(), Poem.updated_at.desc()
    ).limit(current_app.config['FLASK_POEMS_PER_PAGE']).all()

    return render_template('poems/poet.html', **context)


@poems.route('/poems/<string:poem_id>/edit', methods=['GET', 'POST'])
@is_poet
def edit_poem(poem_id):
    """Edit poem (with given id) title and description."""
    # get poem by id
    poem = Poem.find_by(id=poem_id, one=True)
    # get category
    category = Category.find_by(id=poem.category_id, one=True)
    # initialize form
    form = PoemForm(category=category.name, obj=poem)

    if form.validate_on_submit():
        # update poem
        form.populate_obj(poem)
        poem.category_id = Category.get_id(form.category.data)
        # persist to database
        poem.save()
        # redirect to poems
        flash('Poem has been updated successfully.', 'info')
        return redirect(url_for('.poem', poem_id=poem_id))
    return render_template('poems/create_poem.html', form=form, update=True)


@poems.get('/poems/<string:poem_id>/delete')
@is_poet
def delete_poem(poem_id):
    """ Delete a poem and all the associated stanzas. """
    if not can_manage_poem(poem_id):
        flash('Don\'t be a sly; you cannot remove what you didn\'t create!',
              'error')
        return redirect(url_for('.poem', poem_id=poem_id))

    # get poem
    poem = Poem.find_by(id=poem_id, one=True)
    # delete poem
    poem.delete()
    # redirect to dashboard home
    flash('Deletion successfully; what a courage!', 'info')
    return redirect(url_for('.index'))


@poems.route('/poems/<string:poem_id>/add_stanza', methods=['GET', 'POST'])
@is_poet
def add_stanza(poem_id):
    """Add new stanza to poem with given id."""
    if not can_manage_poem(poem_id):
        flash('You are not the author of this poem, hence, edit is restricted',
              'error')
        return redirect(url_for('.poem', poem_id=poem_id))

    poem = Poem.find_by(id=poem_id, one=True)

    # create form
    form = StanzaForm()
    form.index.data = poem.stanzas.count() + 1

    if form.validate_on_submit():
        stanza = Stanza.find_by(index=form.index.data, poem_id=poem_id,
                                one=True)

        if stanza:
            flash(f'Stanza {stanza.index} already exists in poem.', 'error')
        else:
            Stanza.create(
                index=form.index.data,
                content=form.content.data,
                poem_id=poem_id
            )

            flash(f'Stanza {form.index.data} has been added successfully.',
                  'info')

        return redirect(url_for('.poem', poem_id=poem_id))

    return render_template('poems/add_stanza.html', form=form)


@poems.get('/poems/<string:poem_id>/stanzas/<string:stanza_id>/delete')
@is_poet
def delete_stanza(poem_id, stanza_id):
    """Remove a stanza from a poem."""
    if not can_manage_poem(poem_id):
        flash('You are not the author of this poem, hence, edit is restricted',
              'error')
        return redirect(url_for('.poem', poem_id=poem_id))

    stanza = Stanza.find_by(id=stanza_id, poem_id=poem_id, one=True)

    if not stanza:
        flash(f'Stanza {stanza_id} not found in poem or poem id does '
              'not exist.', 'error')
        return redirect(url_for('.index'))

    # delete stanza from poem.
    stanza.delete()

    # redirect to the poem page
    flash(f'Successfully deleted stanza {stanza.index} from poem.', 'info')
    return redirect(url_for('.poem', poem_id=poem_id))


@poems.route('/poems/<string:poem_id>/stanzas/<string:stanza_id>/edit',
             methods=['GET', 'POST'])
@is_poet
def edit_stanza(poem_id, stanza_id):
    """Edit stanza of poem with given id."""
    if not can_manage_poem(poem_id):
        flash('You are not the author of this poem, hence, edit is restricted',
              'error')
        return redirect(url_for('.poem', poem_id=poem_id))

    stanza = Stanza.find_by(id=stanza_id, poem_id=poem_id, one=True)

    if not stanza:
        flash('Stanza was not found, hence cannot be edited.', 'error')
        return redirect(url_for('.index'))

    # create and populate form
    form = StanzaForm(obj=stanza)

    if form.validate_on_submit():
        form.populate_obj(stanza)
        # save edits
        stanza.save()

        flash(f'Successfully updated stanza {stanza.index}.', 'info')
        return redirect(url_for('.poem', poem_id=poem_id))

    return render_template('poems/add_stanza.html', form=form, update=True)


@poems.get('/poems/<string:poem_id>/comments/<string:comment_id>/delete')
@login_required
def delete_comment(poem_id, comment_id):
    """Remove a comment from a poem."""
    comment = Comment.find_by(comment_id=comment_id, one=True)

    if current_user.id != comment.user_id:
        flash('You are not authorized to delete this comment', 'error')
    else:
        comment.delete()
        flash('Deleted comment successfully', 'info')

    # return user to the poem page
    return redirect(url_for('.poem', poem_id=poem_id))


@poems.get('/poems/<string:poem_id>/publish')
@is_poet
def publish_poem(poem_id):
    """Publish or unpublish the poem with given id."""
    if not can_manage_poem(poem_id):
        flash('You are not the author of this poem, hence, edit is restricted',
              'error')
        return redirect(url_for('.poem', poem_id=poem_id))

    # fetch poem by id
    poem = Poem.find_by(id=poem_id, one=True)
    # publish poem
    poem.publish()
    published = 'PUBLISHED' if poem.published else 'UNPUBLISHED'
    # redirect to
    flash('Successfully published poem for the world to see!' if poem.published
          else 'Poem has been unpublished')

    return redirect(url_for('.poem', poem_id=poem_id))


@poems.get('/poems/<string:poem_id>/complete')
@is_poet
def complete_poem(poem_id):
    """Publish or unpublish the poem with given id."""
    if not can_manage_poem(poem_id):
        flash('You are not the author of this poem, hence, edit is restricted',
              'error')
        return redirect(url_for('.poem', poem_id=poem_id))

    # fetch poem by id
    poem = Poem.find_by(id=poem_id, one=True)

    # toggle completed attribute and persist to db
    poem.completed = False if poem.completed else True
    poem.save()
    # set flash message
    flash_msg_type = 'complete' if poem.completed else 'incomplete'
    flash(f'Poem has been marked as {flash_msg_type}.')

    return redirect(url_for('.poem', poem_id=poem_id))


# Add endpoints for the views
poems.add_url_rule('/', view_func=IndexView.as_view('index'), methods=['GET'])
poems.add_url_rule('/search', view_func=SearchPoemsView.as_view('search'), methods=['GET', 'POST'])
