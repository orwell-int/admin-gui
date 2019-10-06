import graphene
from graphene_tornado.schema import QueryRoot
from graphene_tornado.schema import Schema
from graphene_tornado.schema import MutationRoot


class Server(graphene.ObjectType):
    name = graphene.String()
    up = graphene.Boolean()


class MyQueryRoot(QueryRoot):
    server = graphene.Field(Server)

    def resolve_server(self, info):
        print("resolve_server(" + str(info) + ")")
        return Server(name="toto", up=False)


schema = Schema(query=MyQueryRoot, mutation=MutationRoot)
