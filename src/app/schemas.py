from marshmallow import Schema, fields, validates, ValidationError


class DocumentSchema(Schema):
    """DocumentSchema:

            id: string,
            text: string (length less than 10,000 characters),
            language: One of ["en"]
    """
    id = fields.String(required=True)
    text = fields.String(required=True)
    language = fields.String(required=True)

    @validates('text')
    def validate_text(self, value):
        if len(value) > 10000:
            raise ValidationError('Document length must be less than 10,000 characters')

    @validates('language')
    def validate_language(self, value):
        if value != 'en':
            raise ValidationError('English (en) is the only supported language in preview')


class DocumentsSchema(Schema):
    documents = fields.Nested(DocumentSchema, many=True, required=True)


class MatchSchema(Schema):
    start = fields.Integer(required=True)
    end = fields.Integer(required=True)
    label = fields.String(required=True)
    text = fields.String(required=True)


class ServiceSchema(Schema):
    serviceName = fields.String(required=True)
    serviceShortDescription = fields.String(required=True)
    serviceUri = fields.Url(required=True)
    serviceCategories = fields.List(fields.String(), required=True)
    relatedServices = fields.List(fields.String(), required=True)
    matches = fields.Nested(MatchSchema, many=True, required=True)


class DocumentServicesSchema(Schema):
    id = fields.String(required=True)
    cloudServices = fields.Nested(ServiceSchema, many=True, required=True)


class ServicesResponseSchema(Schema):
    documents = fields.Nested(DocumentServicesSchema, many=True, required=True)
