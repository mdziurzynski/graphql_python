import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import authenticate


from users.models import User


def get_user(info):
    token = info.context.session.get('token')

    if not token:
        return

    try:
        user = User.objects.get(token=token)
        return user
    except:
        raise Exception('User not found!')


class UserType(DjangoObjectType):
    class Meta:
        model = User


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    me = graphene.Field(UserType)

    def resolve_users(self, info, **kwargs):
        return User.objects.all()

    def resolve_me(self, info, **kwargs):
        user = get_user(info)
        if not user:
            raise Exception('Not logged!')
        else:
            return user


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = User(
            username=username,
            email=email)

        user.set_password(password)
        user.save()

        return CreateUser(user=user)


class LogIn(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String()
        password = graphene.String()

    def mutate(self, info, username, password):
        user = authenticate(username=username, password=password)

        if not user:
            raise Exception('Invalid username of password!')

        info.context.session['token'] = user.token
        return LogIn(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    login = LogIn.Field()
