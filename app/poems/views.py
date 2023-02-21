from flask import (render_template, redirect, request,
                   flash, url_for, current_app)
from flask_login import login_required, current_user
from . import poems
from .. import db
from .forms import CreatePoemForm
from .forms import AddCategoryForm
from .forms import StanzaForm
from .forms import CreateCommentForm
from ..models import Admin, Poem, Category, Stanza, Comment
from ..utils import is_admin, get_category_choices, get_category_id


@poems.get('/poems')
def index():
    """Fetch all the poems from the database and send to user."""
    # get query params
    category = request.args.get('category', '', type=str)
    page = request.args.get('page', 1, type=int)
    # get all categories names
    category_names = db.session.query(Category.name).all()
    # data to be passed to template
    context = {
        'all_category_names': [c[0] for c in category_names],
        'pagination': None,
        'poems': None,
        'categories': None,
    }
    # create pagination object from poems
    query_poems = db.session.query(Poem).join(
        Category, Category.id == Poem.category_id
    )

    if current_user.is_anonymous or not current_user.is_admin:
        query_poems = query_poems.filter(Poem.published == True)

    if category:
        query_poems = query_poems.filter(Category.name == category)

    context['pagination'] = query_poems.order_by(
        Poem.crafted_on.desc()).paginate(
        page=page, per_page=current_app.config['FLASK_POEMS_PER_PAGE'],
        error_out=False
    )
    # get poems from pagination object and update context
    context['poems'] = context['pagination'].items

    return render_template('poems/index.html', **context)


@poems.route('/categories/new', methods=['GET', 'POST'])
@is_admin
def create_category():
    """Add new category."""
    form = AddCategoryForm()

    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data
        )

        db.session.add(category)
        db.session.commit()

        flash(f'Created a new category ({category.name}).', 'info')
        return redirect(url_for('.create_poem'))
    return render_template('poems/create_category.html', form=form)


@poems.route('/poems/new', methods=['GET', 'POST'])
@is_admin
def create_poem():
    """Create a new poem."""
    # initialize create poem form
    form = CreatePoemForm()
    # add choices to category field dynamically
    form.category.choices = get_category_choices(Category, db)

    if form.validate_on_submit():
        admin = Admin.query.filter_by(user_id=current_user.id).first()
        category = Category.query.filter_by(name=form.category.data).first()
        poem = Poem(
            author_id=admin.id,
            title=form.title.data,
            description=form.description.data,
            category_id=category.id,
            premium=form.is_premium.data
        )
        # persist to database
        db.session.add(poem)
        db.session.commit()
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
    }

    # Get poem stanzas order by stanza index
    context['stanzas'] = context['poem'].stanzas.order_by(Stanza.index).all()

    if not context['poem'].published:
        if current_user.is_anonymous or not current_user.is_admin:
            flash('This poem has not been published yet.', 'error')
            return redirect(url_for('.index'))

    context['form'] = CreateCommentForm()

    if context['form'].validate_on_submit():
        comment = Comment(
            user_id=current_user.id,
            poem_id=poem_id,
            comment=context['form'].comment.data
        )

        db.session.add(comment)
        db.session.commit()

        flash('Comment posted successfully; unapproved yet by poem author.',
              'info')
        return redirect(url_for('.poem', poem_id=poem_id))

    if (current_user.is_anonymous or not current_user.is_admin) \
            and context['poem'].premium:
        flash('Sorry, this poem is only available to premium users.', 'error')
        return redirect(url_for('.index'))

    return render_template('poems/poem.html', **context)


@poems.route('/poems/<string:poem_id>/edit', methods=['GET', 'POST'])
@is_admin
def edit_poem(poem_id):
    """Edit poem (with given id) title and description."""
    poem = Poem.query.get_or_404(poem_id, 'Poem with such id was not found.')
    # initialize form
    form = CreatePoemForm(obj=poem)
    # add choices to category field dynamically
    form.category.choices = get_category_choices(Category, db)

    if form.validate_on_submit():
        # update poem
        form.populate_obj(poem)
        poem.category_id = get_category_id(Category, form.category.data)
        # persist to database
        db.session.add(poem)
        db.session.commit()

        # redirect to poems
        flash('Poem has been updated successfully.', 'info')
        return redirect(url_for('.poem', poem_id=poem_id))
    return render_template('poems/create_poem.html', form=form, update=True)


@poems.get('/poems/<string:poem_id>/delete')
@is_admin
def delete_poem(poem_id):
    """Delete a poem and all the associated stanzas."""
    poem = Poem.query.get_or_404(poem_id, 'Poem with such id not found.')
    db.session.delete(poem)
    db.session.commit()

    flash('Deletion successfully; what a courage!', 'info')
    return redirect(url_for('.index'))


@poems.route('/poems/<string:poem_id>/add_stanza', methods=['GET', 'POST'])
@is_admin
def add_stanza(poem_id):
    """Add new stanza to poem with given id."""
    poem = Poem.query.get_or_404(poem_id, 'Poem with such id does not exist.')

    form = StanzaForm()
    form.index.data = poem.stanzas.count() + 1

    if form.validate_on_submit():
        stanza = Stanza.query.filter_by(
            index=form.index.data, poem_id=poem_id).first()

        if not stanza:
            stanza = Stanza(
                index=form.index.data,
                content=form.content.data,
                poem_id=poem_id
            )

            db.session.add(stanza)
            db.session.commit()
            flash(
                f'Stanza {stanza.index} has been added successfully.', 'info')
        else:
            flash(f'Stanza {stanza.index} already exists in poem.', 'error')
        return redirect(url_for('.poem', poem_id=poem_id))

    return render_template('poems/add_stanza.html', form=form)


@poems.get('/poems/<string:poem_id>/stanzas/<string:stanza_id>/delete')
@is_admin
def delete_stanza(poem_id, stanza_id):
    """Delete a stanza from a poem."""
    stanza = Stanza.query.filter_by(
        id=stanza_id, poem_id=poem_id).first()

    if not stanza:
        flash(f'Stanza {stanza_id} not found in poem or poem id does '
              'not exist.', 'error')
        return redirect(url_for('.index'))

    db.session.delete(stanza)
    db.session.commit()

    flash(f'Successfully deleted stanza {stanza.index} from poem.', 'info')
    return redirect(url_for('.poem', poem_id=poem_id))


@poems.route('/poems/<string:poem_id>/stanzas/<string:stanza_id>/edit',
             methods=['GET', 'POST'])
@is_admin
def edit_stanza(poem_id, stanza_id):
    """Edit stanza of poem with given id."""
    stanza = Stanza.query.filter_by(id=stanza_id, poem_id=poem_id).first()

    if not stanza:
        flash('Stanza was not found, hence cannot be edited.', 'error')
        return redirect(url_for('.index'))

    form = StanzaForm(obj=stanza)

    if form.validate_on_submit():
        form.populate_obj(stanza)

        db.session.add(stanza)
        db.session.commit()

        flash(f'Successfully updated stanza {stanza.index}.', 'info')
        return redirect(url_for('.poem', poem_id=poem_id))

    return render_template('poems/add_stanza.html', form=form, update=True)


@poems.get('/poems/<string:poem_id>/comments/<string:comment_id>/delete')
@login_required
def delete_comment(poem_id, comment_id):
    """Delete a comment from a poem."""
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
@is_admin
def publish_poem(poem_id):
    """Publish or unpublish the poem with given id."""
    poem = Poem.query.get_or_404(poem_id, 'Poem with such id was not found')

    if poem.published:
        poem.published = False
        flash('Poem has been unpublished')
    else:
        poem.published = True
        flash('Successfully published poem for the world to see!')

    db.session.add(poem)
    db.session.commit()

    return redirect(url_for('.poem', poem_id=poem_id))


@poems.get('/poems/<string:poem_id>/complete')
@is_admin
def complete_poem(poem_id):
    """Publish or unpublish the poem with given id."""
    poem = Poem.query.get_or_404(poem_id, 'Poem with such id was not found')

    # toggle completed attribute and persist to db
    poem.completed = False if poem.completed else True
    db.session.add(poem)
    db.session.commit()
    # Set flash message
    flash_msg_type = 'complete' if poem.completed else 'incomplete'
    flash(f'Poem has been marked as {flash_msg_type}.')

    return redirect(url_for('.poem', poem_id=poem_id))
