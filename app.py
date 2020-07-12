from flask import Flask
from flask_cors import CORS
from flask_graphql import GraphQLView
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from controller import Base
from graphqlserver import schema

engine = create_engine('sqlite:///data.sqlite3', convert_unicode=True)
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
Base.metadata.create_all(engine)

app = Flask(__name__)
app.debug = True
CORS(app)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        get_context=lambda: {'session': session},
        graphiql=True  # for having the GraphiQL interface
    )
)


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


if __name__ == '__main__':
    app.run()
