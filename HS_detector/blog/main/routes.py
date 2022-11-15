from flask import render_template,request,Blueprint
from blog.users.forms import SearchForm
from blog.models import Post

main = Blueprint('main', __name__)


@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)#pagination and post order
    return render_template('home.html', posts=posts)


@main.route("/about")
def about():
    return render_template('about.html', title='About')

@main.context_processor
def home():
    form = SearchForm()
    return dict(form=form)