from flask import (render_template, redirect, request,
                   flash, url_for, current_app)
from flask_login import login_required, current_user
from . import poems
from .. import db
from .forms import (PoemForm, CategoryForm, StanzaForm,
                    CommentForm)
from ..models import Poet, Poem, Category, Stanza, Comment
from ..utils import is_poet, can_manage_poem


@poems.get('/poems')
def index():
    """Fetch all the poems from the database and send to user."""
    # get query params
    category = request.args.get('category', '', type=str)
    page = request.args.get('page', 1, type=int)
    # data to be passed to template
    context = {
        'all_category_names': [c.name for c in Category.find_all()],
        'pagination': None,
        'poems': None,
    }
    # create pagination object from poems
    query_poems = db.session.query(Poem).join(
        Category, Category.id == Poem.category_id
    )

    if current_user.is_anonymous or not current_user.is_poet:
        query_poems = query_poems.filter(Poem.published == True)
    else:
        query_poems = query_poems.filter(
            ((Poem.author_id == Poet.find_by(
                user_id=current_user.id, one=True).id) & (Poem.published == False))
            | (Poem.published == True)
        )

    if category:
        query_poems = query_poems.filter(Category.name == category)

    context['pagination'] = query_poems.order_by(
        Poem.author_id.desc(), Poem.created_at.desc()).paginate(
        page=page, per_page=current_app.config['FLASK_POEMS_PER_PAGE'],
        error_out=False
    )
    # get poems from pagination object and update context
    context['poems'] = context['pagination'].items

    return render_template('poems/index.html', **context)


@poems.route('/categories/new', methods=['GET', 'POST'])
@is_poet
def create_category():
    """Add new category."""
    form = CategoryForm()

    if form.validate_on_submit():
        Category.create(name=form.name.data,
                        description=form.description.data)

        flash(f'Created a new category ({form.name.data}).', 'info')
        return redirect(url_for('.create_category'))
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
                    premium=form.is_premium.data)
        poem.save()
        # redirect to poem page
        flash('Successfully created poem. What a courage!', 'info')
        return redirect(url_for('.poem', poem_id=poem.id))
    return render_template('poems/create_poem.html', form=form)


@poems.route('/poems/<string:poem_id>', methods=['GET', 'POST'])
def poem(poem_id):
    """Show details about poem with given id."""
    context = {
        'poem': Poem.query.get_or_404(poem_id,
                                      'Poem with such id not found.'),
        'form': CommentForm(),
        'stanzas': Stanza.find_order_by(Stanza.index, poem_id=poem_id)
    }

    if current_user.is_anonymous and context['poem'].premium:
        flash('Sorry, this poem is only available to registered users.', 'error')
        return redirect(url_for('.index'))

    if not context['poem'].published:
        if current_user.is_anonymous or not context['poem'].is_accessible:
            flash('This poem has not been published yet.', 'error')
            return redirect(url_for('.index'))

    if context['form'].validate_on_submit():
        Comment.create(
            user_id=current_user.id,
            poem_id=poem_id,
            comment=context['form'].comment.data
        )

        flash('Comment posted successfully; you will be notified once approved.',
              'info')
        return redirect(url_for('.poem', poem_id=poem_id))

    return render_template('poems/poem.html', **context)


@poems.route('/poems/<string:poem_id>/edit', methods=['GET', 'POST'])
@is_poet
def edit_poem(poem_id):
    """Edit poem (with given id) title and description."""
    # get poem by id
    poem = Poem.find_by(id=poem_id, one=True)
    # initialize form
    form = PoemForm(obj=poem)

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
    poem = Poem.find_by(poem_id=poem_id, one=True)
    # delete poem
    poem.delete()

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
    comment = Comment.query.get_or_404(comment_id,
                                       'Comment not found, hence cannot be deleted')

    if current_user.id != comment.user_id:
        flash('You cannot delete a comment you did not made.', 'error')
    else:
        db.session.delete(comment)
        db.session.commit()

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

    poem.publish()
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
