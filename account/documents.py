from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Account

@registry.register_document
class AccountDocument(Document):
    class Index:
        # Name of the Elasticsearch index
        name = 'accounts'
        # Optional settings
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Account  # The model associated with this document

        # The fields of the model you want to index
        fields = [
            'account_id',
            'account_name',
            'email',
            'created_at',
        ]
