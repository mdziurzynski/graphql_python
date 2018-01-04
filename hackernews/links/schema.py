import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q

from links.models import Link, Vote
from users.schema import UserType, get_user


class LinkType(DjangoObjectType):

    vote_count = graphene.Int(source='vote_count')

    class Meta:
        model = Link


class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


class Query(graphene.ObjectType):
    # links is the field name
    links = graphene.List(
        LinkType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int()
    )
    votes = graphene.List(VoteType)

    def resolve_links(self, info, search=None, first=None, skip=None, **kwargs):
        qs = Link.objects.all()

        if search:
            filter_statement = (
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
            qs = qs.filter(filter_statement)
        
        if skip:
            qs = qs[skip::]
        if first:
            qs = qs[:first]
        print(qs[0].vote_count)
        return qs

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()


class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = get_user(info)

        if not user:
            raise Exception("You must be logged in in order to vote!")

        link = Link.objects.filter(id=link_id).first()

        if not link:
            raise Exception("Not a valid link!")

        new_vote = Vote.objects.create(
            user=user,
            link=link)

        return CreateVote(
            user=new_vote.user,
            link=new_vote.link)


class CreateLink(graphene.Mutation):
    id = graphene.Int()
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        user = get_user(info) or None

        link = Link(url=url, description=description, posted_by=user)
        link.save()

        return CreateLink(
            id=link.id,
            url=link.url,
            description=link.description,
            posted_by=link.posted_by,
            )


class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()