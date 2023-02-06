"""Contains the app views."""
from flask import render_template, redirect, request, flash, url_for
from . import db, app
from flask_login import login_required, login_user, logout_user, current_user
from .forms.login import LoginForm
from .forms.signup import SignupForm
from .forms.create_poem import CreatePoemForm
from .forms.add_category import AddCategoryForm
from .forms.add_stanza import AddStanzaForm
from .models import User, Admin, Poem, Category, Stanza

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
@login_required
def show_poems():
    """Fetch all the poems from the database and send to authenticated user."""
    poems = Poem.query.all()
    return render_template('poems/poems.html', poems=poems)


@app.route('/categories/new', methods=['GET', 'POST'])
@login_required
def add_category():
    """Add new category."""
    if not current_user.is_admin:
        flash('You are not authorized to access this page.')
        return redirect(url_for('create_poem'))
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
def create_poem():
    """Create a new poem."""
    if not current_user.is_admin:
        flash('You are not unauthorized to access this page.')
        return redirect(url_for('show_poems'))
    # initialize create poem form
    form = CreatePoemForm()
    # add choices to category field dynamically
    categories = Category.query.all()
    form.category.choices = [(category.name, category.name.upper()) for category in categories]
    
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
    return render_template('poems/create.html', form=form)


@app.route('/poems/<int:poem_id>', methods=['GET', 'POST'])
@login_required
def show_poem(poem_id):
    """Show details about poem with given id."""
    poem = Poem.query.get(poem_id)

    if not current_user.is_admin and poem.premium:
        flash('This poem is only available to premium users.')
        return redirect(url_for('show_poems'))
    
    return render_template('poems/poem.html', poem=poem)

@app.route('/poems/<int:poem_id>/add_stanza', methods=['GET', 'POST'])
@login_required
def add_stanza(poem_id):
    """Add new stanza to poem with given id."""
    if not current_user.is_admin:
        flash('You are not authorized to access this page.')
        return redirect(url_for('show_poem'))
    
    poem = Poem.query.get(poem_id)
    if not poem:
        flash('Poem with given id does not exist.')
        return redirect(url_for('show_poems'))
    
    form = AddStanzaForm()

    if form.validate_on_submit():
        stanza = Stanza.query.filter_by(index=form.index.data, poem_id=poem_id).first()

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
    return render_template('poems/add_stanza.html', poem=poem, form=form)


@app.get('/poems/<int:poem_id>/stanzas/<int:stanza_id>/delete')
@login_required
def delete_stanza(poem_id, stanza_id):
    """Delete a stanza from a poem."""
    if not current_user.is_admin:
        flash('You are authorized to perform this operation.')
        return redirect(url_for('show_poem', poem_id=poem_id))
    
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
def edit_stanza(poem_id, stanza_id):
    """Edit stanza of poem with given id."""
    if not current_user.is_admin:
        flash('You are authorized to perform this operation.')
        return redirect(url_for('show_poem', poem_id=poem_id))
    
    form = AddStanzaForm()
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
        form.submit.data = 'Update Stanza'

        # fetch poem data from the database
        poem = Poem.query.get(poem_id)
    
    return render_template('poems/add_stanza.html', form=form, poem=poem)
