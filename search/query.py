from .documents import ProductModelDocument, ErrorDocument, UserFixDocument, ManualFixDocument, TechTipDocument
from resolutions.models import CustomFixes, TechTipFix, ManualFix
from django.db.models import Q as DQ
from elasticsearch_dsl import Q as EQ


class Query:
    _original_queries = ' '
    _documents = []
    _found_terms = {}
    _remaining_terms = []

    def __init__(self, original_queries, documents):
        self._original_queries = original_queries
        self._documents = documents
        self._remaining_terms, self._found_terms = self.__extract_terms()

    def __extract_terms(self):
        found_terms = {}
        remaining_terms = []

        for query in self.original_queries:
            if query not in found_terms:
                found_terms[query] = {
                    'models': [],
                    'errors': []
                }
                search_terms = query.split(' ')
                for word in query.split(' '):
                    if '-' in word:
                        word = word.replace('-', ' AND ')
                    found_models = ProductModelDocument.search().query('query_string', query='*' + word + '*',
                                                                       default_field='model_number',
                                                                       analyze_wildcard='true',
                                                                       )
                    if found_models.count():
                        found_terms[query]['models'].append([model for model in found_models])
                        search_terms.remove(word)
                remaining_terms.append(search_terms)

                search_terms = [word.replace('-', ' AND ') for word in search_terms]
                search_terms = ['(' + word + '*' + ')' for word in search_terms]
                found_errors = ErrorDocument.search().query('query_string', query=' '.join(search_terms),
                                                            default_field='error_name',
                                                            analyze_wildcard='true')

                if found_errors.count():
                    found_terms[query]['errors'].append([error for error in found_errors])
        return remaining_terms, found_terms

    def db_resolution_query(self):
        tip_results = {}
        man_results = {}
        custom_results = {}
        for query in self.found_terms:
            if len(self.found_terms[query]['models']) and len(self.found_terms[query]['errors']):
                model_query = DQ()
                error_query = DQ()
                for item in self.found_terms[query]['models']:
                    for model in item:
                        model_query = model_query | DQ(model_id__model_number=model.model_number)
                for item in self.found_terms[query]['errors']:
                    for error in item:
                        error_query = error_query | DQ(repairs_error__error_name=error.error_name)
                tip_results[query] = TechTipFix.objects.filter(model_query).filter(error_query).distinct()
                man_results[query] = ManualFix.objects.filter(model_query).filter(error_query).distinct()
                custom_results[query] = CustomFixes.objects.filter(model_query).filter(error_query).distinct()
        return tip_results, man_results, custom_results

    def error_query(self):
        error_results = {}
        for query in self.found_terms:
            for item in self.found_terms[query]['errors']:
                error_results[query] = []
                for error in item:
                    error_results[query].append(error)
        return error_results

    def model_query(self):
        model_results = {}
        for query in self.found_terms:
            for item in self.found_terms[query]['models']:
                model_results[query] = []
                for model in item:
                    model_results[query].append(model)
        return model_results

    def es_resolutions_query(self, custom_db_results=None, tt_db_results=None, man_db_results=None):
        custom_results = {}
        tt_results = {}
        man_results = {}
        for search_phrase in self._remaining_terms:
            search_phrase = ' '.join(search_phrase)

            if search_phrase not in custom_results:
                filtering_docs = []
                if custom_db_results:
                    for key, values in custom_db_results.items():
                        for document in values:
                            filtering_docs.append(EQ({'simple_query_string': {'query': document.slug,
                                                                              'fields': ['slug'],
                                                                              'default_operator': 'and'}}))
                custom_results[search_phrase] = \
                    UserFixDocument.search().query('bool',
                                                   must={'multi_match':
                                                             {'query': search_phrase,
                                                              'fields': ['symptoms',
                                                                         'steps_to_fix_error'],
                                                              'analyzer': 'search_analyzer'}},
                                                   must_not=filtering_docs)

            if search_phrase not in tt_results:
                filtering_docs = []
                if tt_db_results:
                    for key, values in tt_db_results.items():
                        for tip in values:
                            filtering_docs.append(EQ({'simple_query_string': {'query': tip.tech_tip_number,
                                                                              'fields': ['tech_tip_number'],
                                                                              'default_operator': 'and'}}))
                tt_results[search_phrase] = \
                    TechTipDocument.search().query('bool',
                                                   must={'multi_match':
                                                             {'query': search_phrase,
                                                              'fields': ['tech_tip_number',
                                                                         'tech_tip_title',
                                                                         'tech_tip_content'],
                                                              'analyzer': 'search_analyzer'}},
                                                   must_not=filtering_docs)

            if search_phrase not in man_results:
                filtering_docs = []
                if man_db_results:
                    for key, values in man_db_results.items():
                        for document in values:
                            filtering_docs.append(EQ({'simple_query_string': {'query': document.slug,
                                                                              'fields': ['slug'],
                                                                              'default_operator': 'and'}}))
                man_results[search_phrase] = \
                    ManualFixDocument.search().query('bool',
                                                     must={'match': {'steps_to_fix_error': {
                                                         'query': search_phrase,
                                                         'analyzer': 'search_analyzer'
                                                     }}},
                                                     must_not=filtering_docs)

        return tt_results, man_results, custom_results

    @property
    def found_terms(self):
        return self._found_terms

    @property
    def original_queries(self):
        return self._original_queries

    @property
    def remaining_terms(self):
        return self._remaining_terms

    def __str__(self):
        return 'original queries are {0} and documents are {1}'.format(self._original_queries, self._documents)


def count_dict_results(*args, **kwargs):
    count = 0
    for items in args:
        if not isinstance(items, dict):
            continue
        for keys, values in items.items():
            for value in values:
                count = count + 1
    return count
