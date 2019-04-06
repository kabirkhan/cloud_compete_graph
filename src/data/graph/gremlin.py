import re


class GremlinQueryBuilder:
    """
    Basic functions to build gremlin queries that add vertices and edges
    """
    @classmethod
    def name_to_id(cls, name):
        if '(' in name:
            name = name[name.idx('(') - 1]
        return name.replace(' ', '-')

    @classmethod
    def gremlin_escape(cls, s):
        return s.replace('"', '\\"').replace('$', '\\$')
    
    @classmethod
    def build_upsert_vertex_query(cls, entity_type, properties):
        q = f"""g.V().has("label", "{entity_type}"){cls.get_properties_str(properties, False)}.
                fold().
                coalesce(unfold(),
                         addV("{entity_type}"){cls.get_properties_str(properties)})"""
        return q

    @classmethod
    def build_upsert_edge_query(cls, from_id, to_id, edge_properties):
        label = edge_properties["label"]
        return f"""g.V("{from_id}").as('v').
                    V("{to_id}").
                    coalesce(__.inE("{label}").where(outV().as('v')),
                             addE("{label}").from('v'){cls.get_properties_str(edge_properties)})"""

    @classmethod
    def build_project_clause(cls, prop_names):
        if len(prop_names) > 0:
            project_output = f'.project("{prop_names[0]}"'
            by_output = f'.by("{prop_names[0]}")'
            for n in prop_names[1:]:
                project_output += f', "{n}"'
                by_output += f'.by("{n}")'
            project_output += ')'

        return project_output + by_output
    
    @classmethod
    def get_by_id_query(cls, _id):
        return 'g.V("{}")'.format(_id)
    
    @classmethod
    def get_properties_str(cls, properties, create=True):
        if create:
            query_str = 'property'
        else:
            query_str = 'has'
        
    
        properties_lower = {k.lower():v for k,v in properties.items()}
        
        if "label" in properties_lower:
            del properties_lower["label"]

        output = ""
        for k, v in properties_lower.items():
            if isinstance(v, str):
                output += '.{}("{}", "{}")'.format(query_str, k, v)
            else:
                output += '.{}("{}", {})'.format(query_str, k, v)
        return output
