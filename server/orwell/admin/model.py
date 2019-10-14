import graphene
#from graphene_tornado.schema import QueryRoot
from graphene_tornado.schema import Schema
from graphene_tornado.schema import MutationRoot
from tornado.escape import to_unicode
import rx


class MyObservable(rx.Observable):
    def subscribe(self, observer):
        ob = rx.Observer()


class Server(graphene.ObjectType):
    name = graphene.String()
    up = graphene.Boolean()


class MyQueryRoot(graphene.ObjectType):
    server = graphene.Field(Server)
    thrower = graphene.String(required=True)
    request = graphene.String(required=True)
    test = graphene.String(who=graphene.String())

    def resolve_thrower(self, info):
        raise Exception("Throws!")

    def resolve_request(self, info):
        return to_unicode(info.context.arguments['q'][0])

    def resolve_server(self, info):
        print("resolve_server(" + str(info) + ")")
        return server

    def resolve_test(self, info, who=None):
        return 'Hello %s' % (who or 'World')


class MyMutationRoot(graphene.ObjectType):
    write_test = graphene.Field(MyQueryRoot)

    def resolve_write_test(self, info):
        return MyQueryRoot()


class MySubscriptionRoot(graphene.ObjectType):
    write_test = graphene.Field(MyQueryRoot)
    server = graphene.Field(Server)

    def resolve_write_test(self, info):
        return MyQueryRoot()

    def resolve_request(self, info):
        print("subscription::resolve_request(" + str(info) + ")")
        return to_unicode(info.context.arguments['q'][0])

    def resolve_server(self, info):
        print("subscription::resolve_server(" + str(info) + ")")
        return server

#    def resolve_server(self, args, context, info):
#        print("subscription::resolve_server(" + str(args) + ", " +
#              str(context) + ", " + str(info) + ")")
#        return server


schema = Schema(
    query=MyQueryRoot,
    mutation=MyMutationRoot,
    subscription=MySubscriptionRoot)

server = Server(name="ServerGame", up=False)
