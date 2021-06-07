from flask import request
from graphql_server.flask import GraphQLView
import graphene
from napoleon.generators.graphql_generator import GraphQLModel
from napoleon.encoders.graph_encoder import GraphQLEncoder
from napoleon.decoders.graph_merger import GraphQLMerger
from napoleon.properties import AbstractObject, Boolean


class ContextedGraphQLView(GraphQLView):

    context = None

    def get_context(self):
        return {"context": self.context, "request": request}


class GrapQLViewBuilder(AbstractObject):

    auto_camelcase: bool = Boolean(default=True)
    pretty = Boolean(default=True)
    graphiql = Boolean(default=True)

    def view(self, instance, endpoint):
        model = GraphQLModel()
        model.generate_output_model(instance.__class__)
        model.generate_input_model(instance.__class__)
        encoder = GraphQLEncoder(model)
        merger = GraphQLMerger(model)

        class Query(graphene.ObjectType):

            root = graphene.Field(model.output_root)

            @staticmethod
            def resolve_root(_root, info):  # noqa
                return encoder.encode(info.context.get("context"))

        class UpdateMutation(graphene.Mutation):

            class Arguments:
                root = model.input_root

            ok = graphene.Boolean()

            @staticmethod
            def mutate(_root, info, root):
                ok = True
                try:
                    merger.decode_update(info.context.get("context"), root)
                except Exception as e:
                    self.log.error(f"Error while updating the object: {instance}, {e}")
                    ok = False
                return ComponentUpdate(ok=ok)  # noqa

        class Mutator(graphene.ObjectType):

            update = UpdateMutation.Field()

        schema = graphene.Schema(query=Query,
                                 mutation=Mutator,
                                 types=list(model.map_classes.values()),
                                 auto_camelcase=self.auto_camelcase)

        return ContextedGraphQLView.as_view(endpoint,
                                            schema=schema,
                                            pretty=self.pretty,
                                            graphiql=self.graphiql,
                                            context=instance)

