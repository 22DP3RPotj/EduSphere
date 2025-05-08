import graphene
# from graphene.validation import DisableIntrospection, depth_limit_validator
# from graphql import validate, parse, GraphQLError
from .queries import Query
from .mutations import Mutation

schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
)

# validation_errors = validate(
#     schema=schema.graphql_schema,
#     document_ast=parse("{ user(id: 1) { name email } }"),
#     rules=(
#         DisableIntrospection,
#         depth_limit_validator(10),
#     )
# )

# if validation_errors:
#     raise GraphQLError("GraphQL validation failed", extensions={"errors": validation_errors})
