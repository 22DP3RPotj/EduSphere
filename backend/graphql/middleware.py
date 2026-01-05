import json
from graphql import parse, validate, GraphQLError
from graphene.validation import DisableIntrospection, depth_limit_validator
from graphql import GraphQLResolveInfo


class ValidationMiddleware:
    def resolve(self, next_, root, info: GraphQLResolveInfo, **kwargs):
        try:
            body = getattr(info.context, "body", None)
            if not body:
                return next_(root, info, **kwargs)

            data = json.loads(body.decode())
            query_str = data.get("query")
            if not query_str:
                return next_(root, info, **kwargs)

            document_ast = parse(query_str)

            errors = validate(
                schema=info.schema,
                document_ast=document_ast,
                rules=(
                    DisableIntrospection,
                    depth_limit_validator(10),
                ),
            )

            if errors:
                raise GraphQLError(
                    "GraphQL validation failed",
                    extensions={"errors": [str(e) for e in errors]},
                )

        except json.JSONDecodeError:
            pass
        except Exception:
            return next_(root, info, **kwargs)

        return next_(root, info, **kwargs)
