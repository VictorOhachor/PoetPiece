"""Contains the app views."""
from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required, login_user, logout_user, current_user

from . import db, app
from .forms.login import LoginForm
from .forms.signup import SignupForm
from .forms.poem import CreatePoemForm
from .forms.add_category import AddCategoryForm
from .forms.stanza import StanzaForm
from .forms.comment import CreateCommentForm
from .models import User, Admin, Poem, Category, Stanza, Comment
from .utils import is_admin

# create new session
session = db.session


@app.route('/')
def index():
    """Implement Index View."""
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Implement Login View."""
    form = LoginForm()

    if current_user.is_authenticated:
        flash('Automatically logged you in.')
        return redirect(url_for('show_poems'))

    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('show_poems')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Log user out of the session."""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Implement Sign up View."""
    form = SignupForm()
    models = {}  # contains the User (and perhaps Admin) instance(s)

    if form.validate_on_submit():
        is_admin = form.is_admin.data

        models['user'] = User(username=form.username.data,
                              password=form.password.data,
                              birth_date=form.birth_date.data)

        if is_admin:
            # retrieve email and gender date
            email = form.email.data
            gender = form.gender.data

            if not (email and gender):
                flash('Email and gender are required for an admin account.')
                return redirect(url_for('signup'))

            if Admin.reached_admin_count():
                flash('Restricted: The number of registered admins has reached limit.')
                return redirect(url_for('signup'))

            models['admin'] = Admin(
                email=email,
                gender=gender,
                users=models['user']
            )
            models['user'].is_admin = True
        db.session.add_all(models.values())
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('login'))
    return render_template('auth/signup.html', form=form)


@app.get('/poems')
def show_poems():
    """Fetch all the poems from the database and send to user."""
    # get query params
    category = request.args.get('category', '', type=str)
    page = request.args.get('page', 1, type=int)

    # get all categories names
    category_names = session.query(Category.name).all()

    # data to be passed to template
    context = {
        'all_category_names': [c[0] for c in category_names],
        'pagination': None,
        'poems': None,
        'categories': None,
    }

    # create pagination object from poems
    query_poems = session.query(Poem).join(
        Category, Category.id == Poem.category_id
    )
    if category:
        query_poems = query_poems.filter(Category.name == category)

    context['pagination'] = query_poems.order_by(
        Poem.crafted_on.desc()).paginate(
        page=page, per_page=app.config['FLASK_POEMS_PER_PAGE'],
        error_out=False
    )

    # get poems from pagination object and update context
    context['poems'] = context['pagination'].items

    return render_template('poems/poems.html', **context)


@app.route('/categories/new', methods=['GET', 'POST'])
@login_required
@is_admin
def add_category():
    """Add new category."""
    form = AddCategoryForm()

    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data
        )

        session.add(category)
        session.commit()

        flash(f'Added new category ({category.name}) to existing categories.')
        return redirect(url_for('create_poem'))
    return render_template('poems/add_category.html', form=form)


@app.route('/poems/new', methods=['GET', 'POST'])
@login_required
@is_admin
def create_poem():
    """Create a new poem."""
    # initialize create poem form
    form = CreatePoemForm()
    # add choices to category field dynamically
    form.category.choices = [(category[0], category[0].upper())
                             for category in session.query(Category.name).all()]

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
        session.add(poem)
        session.commit()

        # redirect to poems
        flash('New poem has been created successfully.')
        return redirect(url_for('show_poems'))
    return render_template('poems/poem_form.html', form=form)


@app.route('/poems/<int:poem_id>', methods=['GET', 'POST'])
def show_poem(poem_id):
    """Show details about poem with given id."""
    poem = Poem.query.get_or_404(poem_id, 'Poem with given id was not found.')
    comment_form = CreateCommentForm()

    if comment_form.validate_on_submit():
        comment = Comment(
            user_id=current_user.id,
            poem_id=poem_id,
            comment=comment_form.comment.data
        )

        session.add(comment)
        session.commit()

        flash('Comment added to poem successfully; Not yet approved though.')
        return redirect(url_for('show_poem', poem_id=poem_id))

    if (current_user.is_anonymous or not current_user.is_admin) and poem.premium:
        flash('This poem is only available to premium users.')
        return redirect(url_for('show_poems'))

    return render_template('poems/poem.html', poem=poem, form=comment_form)


@app.route('/poems/<int:poem_id>/edit', methods=['GET', 'POST'])
@is_admin
def edit_poem(poem_id):
    """Edit poem (with given id) title and description."""
    poem = Poem.query.get(poem_id)
    # redirect to /poems if poem id is invalid
    if (not poem):
        flash('Poem with given id was not found.', 'error')
        return redirect(url_for('show_poems'))

    # initialize form
    form = CreatePoemForm(obj=poem)
    # add choices to category field dynamically
    form.category.choices = [(category[0], category[0].upper())
                             for category in session.query(Category.name).all()]

    if form.validate_on_submit():
        # update poem
        form.populate_obj(poem)
        # persist to database
        session.add(poem)
        session.commit()

        # redirect to poems
        flash('Poem has been updated successfully.')
        return redirect(url_for('show_poems'))
    return render_template('poems/poem_form.html', form=form, update=True)


@app.get('/poems/<int:poem_id>/delete')
@login_required
def delete_poem(poem_id):
    """Delete a poem and all the associated stanzas."""
    poem = Poem.query.get_or_404(poem_id, 'Poem with given id not found.')
    session.delete(poem)
    session.commit()

    return redirect(url_for('show_poems'))


@app.route('/poems/<int:poem_id>/add_stanza', methods=['GET', 'POST'])
@login_required
@is_admin
def add_stanza(poem_id):
    """Add new stanza to poem with given id."""
    poem = Poem.query.get(poem_id)
    if not poem:
        flash('Poem with given id does not exist.')
        return redirect(url_for('show_poems'))

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

            session.add(stanza)
            session.commit()
            flash('New stanza has been added successfully.')
        else:
            flash('Poem with given stanza number already exists.')

        return redirect(url_for('show_poem', poem_id=poem_id))
    return render_template('poems/stanza_form.html', form=form)


@app.get('/poems/<int:poem_id>/stanzas/<int:stanza_id>/delete')
@login_required
@is_admin
def delete_stanza(poem_id, stanza_id):
    """Delete a stanza from a poem."""
    stanza = Stanza.query.filter_by(
        id=stanza_id, poem_id=poem_id).first()

    if not stanza:
        flash('Stanza not found in poem with given id.')
        return redirect(url_for('show_poems'))

    session.delete(stanza)
    session.commit()

    flash(f'Deleted stanza number {stanza.index} from poem.')
    return redirect(url_for('show_poem', poem_id=poem_id))


@app.route('/poems/<int:poem_id>/stanzas/<int:stanza_id>/edit', methods=['GET', 'POST'])
@login_required
@is_admin
def edit_stanza(poem_id, stanza_id):
    """Edit stanza of poem with given id."""
    form = StanzaForm()
    stanza = Stanza.query.filter_by(id=stanza_id, poem_id=poem_id).first()

    if form.validate_on_submit():
        stanza.index = form.index.data
        stanza.content = form.content.data

        session.add(stanza)
        session.commit()

        flash(f'Stanza number {stanza.index} has been updated successfully.')
        return redirect(url_for('show_poem', poem_id=poem_id))

    if stanza:
        form.index.data = stanza.index
        form.content.data = stanza.content

    return render_template('poems/stanza_form.html', form=form, update=True)


@app.get('/poems/<int:poem_id>/comments/<int:comment_id>/delete')
@login_required
def delete_comment(poem_id, comment_id):
    """Delete a comment from a poem."""
    comment = Comment.query.get(comment_id)

    if current_user.id != comment.user_id:
        flash('You cannot delete a comment you did not add.',
              'error')
    else:
        session.delete(comment)
        session.commit()

        flash('Deleted comment successfully', 'info')
    # return user to the poem page
    return redirect(url_for('show_poem', poem_id=poem_id))
