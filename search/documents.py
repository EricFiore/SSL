from django_elasticsearch_dsl import Document, Index
from django_elasticsearch_dsl.registries import registry
from resolutions.models import CustomFixes, TechTipFix, ManualFix, Error
from library.models import ProductModel


@registry.register_document
class UserFixDocument(Document):

    class Index:
        name = 'user_fix_index'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'index_analyzer': {
                        'tokenizer': 'standard',
                        'char_filter': ['html_strip'],
                        'filter': ['stop', 'lowercase']
                    },
                    'search_analyzer': {
                        'tokenizer': 'standard',
                        'filter': ['stop', 'lowercase', 'graph_synonyms']
                    }
                },
                'filter': {
                    'graph_synonyms': {
                        'type': 'synonym_graph',
                        'synonyms_path': 'synonym.txt',
                        'updateable': True
                    }
                }
            }
        }
        mappings = {
            'properties': {
                'text': {
                    'type': 'text',
                    'analyzer': 'index_analyzer',
                    'search_analyzer': 'search_analyzer'
                }
            }
        }

    class Django:
        model = CustomFixes

        fields = [
            'slug',
            'symptoms',
            'steps_to_fix_error'
        ]


@registry.register_document
class TechTipDocument(Document):
    class Index:
        name = 'tech_tip_index'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'index_analyzer': {
                        'tokenizer': 'standard',
                        'char_filter': ['html_strip'],
                        'filter': ['stop', 'lowercase']
                    },
                    'search_analyzer': {
                        'tokenizer': 'standard',
                        'filter': ['stop', 'lowercase', 'graph_synonyms']
                    }
                },
                'filter': {
                    'graph_synonyms': {
                        'type': 'synonym_graph',
                        'synonyms_path': 'synonym.txt',
                        'updateable': True
                    }
                }
            }
        }
        mappings = {
            'properties': {
                'text': {
                    'type': 'text',
                    'analyzer': 'index_analyzer',
                    'search_analyzer': 'search_analyzer'
                }
            }
        }

    class Django:
        model = TechTipFix

        fields = [
            'slug',
            'tech_tip_number',
            'tech_tip_title',
            'tech_tip_content',
        ]


@registry.register_document
class ManualFixDocument(Document):

    class Index:
        name = 'manual_fix_index'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'index_analyzer': {
                        'tokenizer': 'standard',
                        'char_filter': ['html_strip'],
                        'filter': ['stop', 'lowercase']
                    },
                    'search_analyzer': {
                        'tokenizer': 'standard',
                        'filter': ['stop', 'lowercase', 'graph_synonyms']
                    }
                },
                'filter': {
                    'graph_synonyms': {
                        'type': 'synonym_graph',
                        'synonyms_path': 'synonym.txt',
                        'updateable': True
                    }
                }
            }
        }
        mappings = {
            'properties': {
                'text': {
                    'type': 'text',
                    'analyzer': 'index_analyzer',
                    'search_analyzer': 'search_analyzer'
                }
            }
        }

    class Django:
        model = ManualFix

        fields = [
            'slug',
            'steps_to_fix_error'
        ]


@registry.register_document
class ErrorDocument(Document):

    class Index:
        name = 'error'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Error

        fields = [
            'slug',
            'error_name',
            'error_title',
            'error_description'
        ]


@registry.register_document
class ProductModelDocument(Document):

    class Index:
        name = 'models'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = ProductModel

        fields = [
            'model_number',
            'slug',
            'model_description'
        ]
